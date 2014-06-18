<?php
$execTimes = array(
    'magic' => 0,
    'custom'=> 0
);
$start = microtime(true);
include 'test.php';
$execTimes['magic'] = microtime(true) - $start;

$start = microtime(true);
include 'after.php';
$execTimes['custom'] = microtime(true) - $start;

printf(
    'Basic example difference is %.5f',
    $execTimes['magic'] - $execTimes['custom']
);
echo PHP_EOL;
