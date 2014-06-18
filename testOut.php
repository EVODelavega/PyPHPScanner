<?php
class Foo3
{
    private $pyTest = null;
    public function __construct($val = 123)
    {
        $this->pyTest = $val;
    }

    public function getPyTest()
    {
        return $this->pyTest;
    }

    public function setPyTest($val)
    {
        $this->pyTest = $val;
        return $this;
    }
}
$start = microtime(true);
for ($i=0;$i<100;++$i)
{
    $foo = new Foo3($i);
    $temp = $foo->getPyTest();
    if ($foo->getPyTest()*$i < 300)
    {
        $foo->setPyTest(456);
    }
}
printf('Loop took %.6fms', microtime(true) - $start);
echo PHP_EOL;
