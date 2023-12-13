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
                $header//tei:correspDesc/tei:correspAction[@type='sent']/tei:date/@when
            case "place-sent" return
                $header//tei:correspAction[@type='sent']/tei:placeName
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
            case "ID" return
                $header//tei:idno[@type eq 'ALMA_NZ']
            default return
                ()
};

declare function idx:get-person-mentions($text as element()) { 
    let $collection := collection($idx:app-root || '/data/Persons')
    let $keys := $text/descendant::tei:rs[@type eq 'person']/@key
    for $key in $keys
    let $persName := $collection/id($key)//tei:persName[@type eq 'reg']
    let $surname := $persName/tei:surname
    return if ($surname/node()) then $surname || ', ' || string-join($surname/following-sibling::*[node()], ' ')
            else string-join($persName/*[node()], ' ')
    };
    
declare function idx:get-place-mentions($text as element()) { 
    let $collection := collection($idx:app-root || '/data/Places')
    let $keys := $text/descendant::tei:rs[@type eq 'place']/@key
    for $key in $keys
    let $placeName := $collection/id($key)//tei:placeName[@xml:lang eq 'de']
    return 
        $placeName
    };
    
declare function idx:get-letter-mentions($text as element()) { 
    let $collection := collection($idx:app-root || '/data/Letters')
    let $keys := $text/descendant::tei:rs[@type eq 'letter']/@key
    for $key in $keys
    let $title := $collection/id($key)//tei:titleStmt//tei:title[@type eq 'main']
    return 
        if ($title) then $title else $key
    };
    
declare function idx:get-work-mentions($text as element()) { 
    let $keys := $text/descendant::tei:rs[@type eq 'biblio']/@key
    let $collection := collection($idx:app-root || '/data/Bibliography')
    for $key in $keys
    let $work := $collection/id($key)
    let $title := if ($work/descendant::tei:analytic) then $work/descendant::tei:analytic/tei:title[1] else  $work/descendant::tei:monographic/tei:title[1]
    let $author := string-join($work//tei:author//tei:surname, ' &amp; ')
    let $date:= $work//descendant::tei:date[1]
    let $formattedAuthor := if ($author) then $author || '. ' else ()
    let $formattedTitle := if ($title) then if (string-length($title) gt 45) then substring($title, 1, 45) || '[…]. ' else $title || '. ' else ()
    let $formatted := $formattedAuthor || $formattedTitle || $date
    return 
        if (string-length($formatted) gt 2) then $formatted else $key
                    
    };

declare function idx:get-genre($header as element()?) {
    for $target in $header//tei:textClass/tei:catRef[@scheme="#genre"]/@target
    let $category := id(substring($target, 2), doc($idx:app-root || "/data/taxonomy.xml"))
    return
        $category/ancestor-or-self::tei:category[parent::tei:category]/tei:catDesc
};
