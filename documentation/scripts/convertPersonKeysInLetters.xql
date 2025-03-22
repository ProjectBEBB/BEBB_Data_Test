xquery version "3.1";

declare namespace tei="http://www.tei-c.org/ns/1.0";

let $letters := collection("/db/apps/bebb-data/Tressan-JIIB")//tei:TEI

for $l in $letters//tei:persName[@key]
    let $nk := translate($l/@key, ")(", "-")
                    let $update :=
                        update value $l/@key with $nk
                       
return $l