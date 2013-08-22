--TEST--
Comments
--FILE--
<?php
require dirname(__FILE__) . '/../bootstrap_tests.php';

snowscript_to_php('
###
Multiline comment
# Should work too.

is very good!#

Still!
###

# Short comment
# Still short
###
Now long
###
class Foo
    ###
    A comment.
    which is long
    ###
    a = false
', 0);
--EXPECT--
<?php
class Foo
{
    

    public function __construct() {
        $this->a = false;
    }

}
