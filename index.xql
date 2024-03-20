xquery version "3.1";

module namespace idx="http://teipublisher.com/index";

declare namespace tei="http://www.tei-c.org/ns/1.0";
declare namespace dbk="http://docbook.org/ns/docbook";

declare variable $idx:app-root :=
    let $rawPath := system:get-module-load-path()
    return
        (: strip the xmldb: part :)
        if (starts-with($rawPath, "xmldb:exist://")) then
            if (starts-with($rawPath, "xmldb:exist://embedded-eXist-server")) then
                substring($rawPath, 36)
            else
                substring($rawPath, 15)
        else
            $rawPath
    ;
    declare variable $idx:bernoullis-ids := ('pers_DE-588-117589144', 'pers_DE-588-119166895', 'pers_DE-588-117589136', 'pers_DE-588-118509969', 
    'pers_DE-588-120475030', 'pers_DE-588-118509950', 'pers_DE-588-119112450', 'pers_DE-588-135542146', 'pers_DE-588-118656503');
    
    declare variable $idx:bernoullis := collection('/db/apps/bebb-data/data/Briefwechsel');

(:~
 : Helper function called from collection.xconf to create index fields and facets.
 : This module needs to be loaded before collection.xconf starts indexing documents
 : and therefore should reside in the root of the app.
 :)
declare function idx:get-metadata($root as element(), $field as xs:string) {
    let $header := $root/tei:teiHeader
    return
        switch ($field)
            case "title" return
                string-join((
                    $header//tei:msDesc/tei:head, $header//tei:titleStmt/tei:title[@type = 'main'],
                    $header//tei:titleStmt/tei:title,
                    $root/dbk:info/dbk:title,
                    $root//article-meta/title-group/article-title,
                    $root//article-meta/title-group/subtitle
                ), " - ")
            case "author" return (
                $header//tei:correspDesc/tei:correspAction/tei:persName,
                $header//tei:titleStmt/tei:author,
                $root/dbk:info/dbk:author,
                $root//article-meta/contrib-group/contrib/name
            )
            case "language" return
                head((
                    $header//tei:langUsage/tei:language/@ident,
                    $root/@xml:lang,
                    $header/@xml:lang
                ))
            case "date" return head((
                $header//tei:correspDesc/tei:correspAction/tei:date/@when,
                $header//tei:sourceDesc/(tei:bibl|tei:biblFull)/tei:publicationStmt/tei:date,
                $header//tei:sourceDesc/(tei:bibl|tei:biblFull)/tei:date/@when,
                $header//tei:fileDesc/tei:editionStmt/tei:edition/tei:date,
                $header//tei:publicationStmt/tei:date
            ))
            case "date-sent" return 
                ($header//tei:correspDesc/tei:correspAction[@type='sent']/tei:date/@when, $header//tei:correspDesc/tei:correspAction[@type='sent']/tei:date/@notBefore)
            case "place-sent" return
                $header//tei:correspAction[@type='sent']/tei:placeName/@key
            case "genre" return (
                idx:get-genre($header),
                $root/dbk:info/dbk:keywordset[@vocab="#genre"]/dbk:keyword
            )
            case "correspondent-id" return 
                $header//tei:correspDesc//tei:persName/@key 
            case "correspondent-name" return (
                $header//tei:correspDesc//tei:persName/text()
            )
            case "correspondent-main" return 
                $header//tei:ptr[@type eq 'Briefwechsel']/@target 
            case "briefwechsel" return
                ($header//tei:ptr[@type eq 'Briefwechsel']/@target, $header//tei:ptr[@type eq 'Korrespondenz']/@target)
            case "briefwechsel-key" return
                $header//tei:correspContext/tei:ref/@target
            case "correspondent-key" return
                $header//tei:correspAction//tei:persName[not(@role eq 'main')]/@key
            case "sender" return
                $header//tei:correspAction[@type eq 'sent']/tei:persName/@key
            case "addressee" return
                $header//tei:correspAction[@type eq 'received']/tei:persName/@key
            case "shelfmark" return
                $header//tei:idno[@type eq 'callNumber']
            case "status" return
                $header//tei:revisionDesc/@status
            case "korrespondenz" return
                $header//tei:ptr[@type eq 'Korrespondenz']/@target
            default return
                ()
};

declare function idx:get-idnos($header as element()) {
    let $idnos := $header//tei:altIdentifier/tei:idno
    let $formatted := for $idno in $idnos return replace($idno/@type, '_', ' ') || ' ' || $idno/string()
    return 
        $formatted
    };


declare function idx:has-facsimile($root as element()) {
    let $facsimile := $root//tei:facsimile/tei:graphic
    return if ($facsimile and not(matches($facsimile/@url, '[Ff]ake'))) then 'yes' else 'no'
    };

declare function idx:get-correspondent($header as element()) {
       $header//tei:correspDesc//tei:persName[not(@key = $idx:bernoullis-ids)]/@key 
    };
    
declare function idx:get-name-main($header as element()) {
   (:  : let $id := $header//tei:ptr[@type eq 'Briefwechsel']/@target
    let $main := $idx:bernoullis/id($id)//tei:persName
    return $main/text():)
    $header//tei:correspDesc//tei:persName[@key = $idx:bernoullis-ids]/text()
    };
    
declare function idx:get-normalizedText($text as element()) {
    let $contents := $text/descendant::tei:div[@type = ('letter', 'attachment')]
    let $textNodes := $contents//text()[not(ancestor::tei:orig)][not(ancestor::tei:pc[@type eq 'hyphenation'])][not(ancestor::tei:abbr)][not(ancestor::tei:note[@type = ('comment', 'editorial')])]
    return
        string-join($textNodes, '')
    };
    
declare function idx:get-diplomaticText($text as element()) {
    let $contents := $text/descendant::tei:div[@type = ('letter', 'attachment')]
    let $textNodes := $contents//text()[not(ancestor::tei:reg)][not(ancestor::tei:expan)][not(ancestor::tei:note[@type = ('comment', 'editorial')])]
    return
        string-join($textNodes, '')
    };
    
declare function idx:get-commentary($text as element(), $context as xs:string) {
    let $comments := ($text/descendant::tei:note[@type = ('editorial', 'comment')], $text/descendant::div[@type eq 'editorialNote'])
    return 
        switch ($context)
            case 'document' return string-join($comments, '&#xA;')
            default return string-join(($comments, $text/ancestor::tei:TEI/tei:teiHeader/descendant::tei:abstract/tei:p), '&#xA;')
        
    };

declare function idx:get-name($person as element()) {
    let $name := $person/tei:persName
    let $var1 := string-join($name/*, ' ')
    let $var2 := if ($name/tei:surname/text()) then $name/tei:surname || ', ' || $name/tei:forename else $name/tei:forename
    return string-join(($var1, $var2), ' ')};



declare function idx:get-genre($header as element()?) {
    for $target in $header//tei:textClass/tei:catRef[@scheme="#genre"]/@target
    let $category := id(substring($target, 2), doc($idx:app-root || "/data/taxonomy.xml"))
    return
        $category/ancestor-or-self::tei:category[parent::tei:category]/tei:catDesc
};
