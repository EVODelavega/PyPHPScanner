<?php
class Foo
{
    private $pyTest = null;
    public function __construct($val = 123)
    {
        $this->pyTest = $val;
    }

    public function __call($method, array $args)
    {
        if (substr($method, 0, 3) == 'set')
        {
            $property = strtolower($method{3}).substr($method, 4);
            if (!property_exists($this, $property))
            {
                return null;
            }
            $this->{$property} = $args[0];
            $method{0} = 'g';//<-- NOT JOKING
        }
        if (substr($method, 0, 3) == 'get')
        {
            $property = strtolower($method{3}).substr($method, 4);
            if (property_exists($this, $property))
            {
                return $this->{$property};
            }
            return null;
        }
        return null;
    }

    public function __get($val)
    {
        $method = 'get'.ucfirst($val);
        return $this->{$method}();
    }

    public function __set($n, $v)
    {
        $method = 'set'.ucfirst($n);
        $this->{$method}($v);
    }
}
$start = microtime(true);
for ($i=0;$i<100;++$i)
{
    $foo = new Foo($i);
    $temp = $foo->pyTest;
    if ($foo->pyTest*$i < 300)
    {
        $foo->pyTest = 456;
    }
}
printf('Loop took %.6fms', microtime(true) - $start);
echo PHP_EOL;
