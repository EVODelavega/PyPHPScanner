<?php
class Foo
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

	public function __get($val)
	{
		if ($val == 'pyTest')
			return $this->pyTest;
	}

	public function __set($n, $v)
	{
		$this->{$n} = $v;
	}
}
$i = new Foo;
$temp = $i->pyTest;

if ($i->pyTest < 300)
{
	$i->pyTest = 456;
}
