--TEST--
Static property fetches
--FILE--
<?php
require dirname(__FILE__) . '/../../bootstrap_tests.php';

snowscript_to_php("
A..b
A..b['c']
", 0);
--EXPECT--
<?php
A::$b;
A::$b['c'];