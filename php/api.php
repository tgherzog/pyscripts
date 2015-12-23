#!/usr/bin/php
<?php

# simple script to return API values in TSV format
# replace field list with "-h" to see field names
# objects will be converted to multiple columns

$fields = explode(',', $argv[1]);
$url = $argv[2];

$show_header = count($fields) == 1 && $fields[0] == '-h';

if( ! $url || count($fields) < 0 ) {
  fprintf(STDERR, "usage: php $argv[0] field1,field2,... url\n");
  exit;
}

# spiff up the url
$parts = parse_url($url);
if( $parts['host'] && strpos($parts['host'],'.') === false  ) {
  $parts['path'] = "$parts[host]$parts[path]";
  unset($parts['host']);
}
parse_str($parts['query'], $query);

$parts = array_merge(array(
  'scheme' => 'http',
  'host' => 'api.worldbank.org',
), $parts);

$query['format'] = 'json';
$query = array_merge(array(
  'per_page' => 9999,
), $query);

if( $show_header ) $query['per_page'] = 1;

$path = explode('/', $parts['path']);
if( $path[0] === '' ) array_shift($path);

if( false && $path[0] !== 'v2' ) {
  # automatically provide version and language
  array_splice($path, 0, 0, array('v2', 'en'));
}

# print_r($parts); print_r($path); print_r($query); exit;
$url = sprintf("%s://%s/%s?%s", $parts['scheme'], $parts['host'], implode('/', $path), http_build_query($query));
# print "$url\n"; exit;
print "$url\n";

$data = file_get_contents($url);
$data = json_decode($data);
$data = $data[1];
# print_r($data); exit;

if( ! is_array($data) ) {
  fprintf(STDERR, "Error: no data returned from API\n");
  exit;
}

foreach($data as $row) {
  $tmp = array();
  if( $show_header ) {
    foreach(array_keys((array) $row) as $fld) {
      $tmp[] = $fld;
    }
    print implode("\t", $tmp) . "\n";
    break;
  }
  foreach($fields as $fld) {
    if( is_object($row->$fld) )
      foreach(array_values((array) $row->$fld) as $x) $tmp[] = $x;
    else
      $tmp[] = $row->$fld;
  }

  print implode("\t", $tmp) . "\n";
}
