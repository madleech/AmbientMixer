<?
	# convert URL into ambient mixer Python
	
	# 1: get URL
	if ($_SERVER['argc'] != 2)
		die("Usage: {$_SERVER['argv'][0]} <url>");
	
	# 2: load URL
	$url = $_SERVER['argv'][1];
	$html = file_get_contents($url);
	
	# 3: look for XML line
	# http://xml.ambient-mixer.com/audio-template?id%5Ftemplate=950
	if (!preg_match("/soundTemplate[ ]*:[ ]*'?([0-9]+)/", $html, $bits))
		die("Could not extract template from HTML");
	else
		$xmlurl = "http://xml.ambient-mixer.com/audio-template?id%5Ftemplate={$bits[1]}";
	
	# 3.5: look for page title
	if (!preg_match("/<title>(.*)<\/title>/", $html, $bits))
		die("Could not extract title from HTML");
	else
		$title = trim(strtr(trim($bits[1]), array('  ' => ' ', 'audio atmosphere' => '')));
	
	
	# 4: load XML
	$xml = file_get_contents($xmlurl);
	
	# 5: parse XML
	# <channel1>
	#  <id_audio>173</id_audio>
	#  <name_audio>Seagulls Call</name_audio>
	#  <url_audio>http://www.ambient-mixer.com/audio/a/e/f/aef4f8e4684ad0238e1a0938e536430f.mp3</url_audio>
	#  <mute>false</mute>
	#  <volume>26</volume>
	#  <balance>-15</balance>
	#  <random>true</random>
	#  <random_counter>2</random_counter>
	#  <random_unit>10m</random_unit>
	#  <crossfade>false</crossfade>
	# </channel1>
	$xml = new SimpleXmlElement($xml);
	$sounds = array();
	for($i=1; $i<=8; $i++) {
		$channel = $xml->{"channel{$i}"};
		
		# empty channel?
		if (!(string) $channel->url_audio) continue;
		
		# 5.0 create filename
		$filename = 'sounds/'.strtolower(strtr($channel->name_audio, array(' '=>'-'))).'.mp3';
		
		# 5.1 download file
		if (!file_exists($filename)) {
			$data = file_get_contents((string) $channel->url_audio);
			file_put_contents($filename, $data);
		}
		
		# 5.2 work out random/loop values
		$loop = $channel->random != 'true';
		$rand = (int) $channel->random_counter;
		if ($loop == false) switch((string) $channel->random_unit) {
			case '1m':  $freq = $rand * 5; break;
			case '10m': $freq = $rand * 1; break;
			case '1h':  $freq = ((float) $rand) * 0.1; break;
		}
		else $freq = 0;
		
		# 5.3 create sound elements
		$sounds[] = (object) array(
			'id'        => $i-1,
			'name'      => (string) $channel->name_audio,
			'filename'  => $filename,
			'volume'    => (int) $channel->volume,
			'frequency' => $freq,
			'loop'      => $loop,
		);
	}
	
	# 6: create result
	$data = (object) array(
		'name' => $title,
		'sounds' => $sounds,
	);
	
	# 7: output JSON
	$json = json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
	$filename = strtolower(strtr($title, array(' ' => '-'))).'.json';
	file_put_contents($filename, $json);
?>