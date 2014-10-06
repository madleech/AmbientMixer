#!/usr/bin/php
<?php

function curl_wrapper($url, $data = null, $headers = null, $opts = array()) {
	$curl = curl_init();
	curl_setopt($curl, CURLOPT_URL, $url);
	curl_setopt($curl, CURLOPT_TIMEOUT, 240);
	curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($curl, CURLOPT_FOLLOWLOCATION, true);
	curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false); 
	curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, false);
	curl_setopt($curl, CURLOPT_HEADER, false);
	curl_setopt($curl, CURLOPT_DNS_USE_GLOBAL_CACHE, true); 
	curl_setopt($curl, CURLOPT_HTTPHEADER, array('Expect:'));
	// optional curl options
	if ($opts) foreach($opts as $k => $v) curl_setopt($curl, $k, $v); 
	// post data
	if ($data !== null) curl_setopt($curl, CURLOPT_POSTFIELDS, $data);
	// extra headers
	if ($headers !== null) curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
	// make request
	$raw_result = curl_exec($curl);
	// catch errors
	if ($raw_result === false && $error = curl_error($curl)) {
		curl_close($curl);
		throw new Exception($error);
	}
	// close & return result
	curl_close($curl);
	return $raw_result;
}

# check input parameters
if ($_SERVER['argc'] <= 1)
	die("Usage: {$_SERVER['argv'][0]} <config.json>");

# get params
$filename = $_SERVER['argv'][1];

# get json
$json = file_get_contents($_SERVER['argv'][1]);

# build data
$data = (object) array(
	"target" => "config",
	"method" => "set",
	"name" => "",
	"args" => [$json]
);

# send data
$result = curl_wrapper("http://localhost:9988/", json_encode($data), array("Content-Type: application/json"));
print_r($result);
?>