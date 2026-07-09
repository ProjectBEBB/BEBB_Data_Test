xquery version "3.1";

(: The following external variables are set by the repo:deploy function :)

(: file path pointing to the exist installation directory :)
declare variable $home external;
(: path to the directory containing the unpacked .xar package :)
declare variable $dir external;
(: the target collection into which the app is deployed :)
declare variable $target external;

declare function local:create-parts-cache-collection() {
    let $collection := $target || "/cache"
    return (
        if (xmldb:collection-available($collection)) then
            ()
        else
            xmldb:create-collection($target, "cache"),
        sm:chown(xs:anyURI($collection), "guest"),
        sm:chgrp(xs:anyURI($collection), "guest"),
        sm:chmod(xs:anyURI($collection), "rwx------")
    )
};

xmldb:create-collection($target, "data"),
sm:chmod(xs:anyURI($target || "/data"), "rwxrwxr-x"),
sm:chown(xs:anyURI($target || "/data"), "tei"),
sm:chgrp(xs:anyURI($target || "/data"), "tei"),
local:create-parts-cache-collection()
