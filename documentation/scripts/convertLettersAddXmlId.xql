xquery version "3.1";

declare namespace tei="http://www.tei-c.org/ns/1.0";

let $letters := collection("/db/apps/bebb-data/Tressan-JIIB")//tei:TEI

for $l in $letters
    let $nk := 'B_' || $l//tei:idno[@type='ALMA']
return 
    update insert attribute xml:id {$nk} into $l