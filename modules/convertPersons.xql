xquery version "3.1";

declare namespace tei="http://www.tei-c.org/ns/1.0";

declare function local:normalize($input as item()*) as item()* {
    
for $node in $input
   return 
      typeswitch($node)
       
        case element()
           return
              element {QName("http://www.tei-c.org/ns/1.0", local-name($node))} {
                for $att in $node/@*
                   return
                      $att
                ,
                for $child in $node/node()
                   return 
                       local:normalize($child)
              }
        default 
            return $node
};

for $d in collection('/db/apps/bebb-data/data/Persons')/*:person
let $tei := local:normalize($d)
return 
    xmldb:store(util:collection-name($d), util:document-name($d), $tei)
,
for $d in collection('/db/apps/bebb-data/data/Places')/*:place
let $tei := local:normalize($d)
return xmldb:store(util:collection-name($d), util:document-name($d), $tei)