<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<?php # PHP Pre-Processing Block
 $array = array();
 foreach (file("stations.txt") as $line) {
	 list($key, $value) = explode(' ', $line, 2) + array(NULL, NULL);
	 if ($value !== NULL) {
		 $array[$key] = $value;
	 }
 }
/* End PHP Pre-Processing Block */ ?>
    <title> <?php echo trim($array["Network"]) ?> LMA </title
    <meta name="Description" content="GUUNGDONG LMA">
    
    <link rel="stylesheet" href="./files/style.css" type="text/css" media="screen">
    <link href="./files/menu-style.css" rel="stylesheet">
  </head>
  <body>
      <div id="header">
        <div id="logo">
          <div id="logo_text">
            <h1><?php echo strtoupper($array["Network"]) ?> LMA</h1>
            <h2><?php echo $array["Network"] ?> Lightning Mapping Array</h2>
			<p>
            <nav>
                <ul>
                    <li> <a target="iframe_a" href="./cal.php">Archive</a></li>
                    <li> <a target="iframe_a" href="./current/current_density_z1_ten.php">Current</a> </li>
                    <li> <a target="iframe_a" href="./current/current_anim_z1.php">Animation</a> </li>
                    <li> <a target="iframe_a" href="./googleearth.php">Google Earth Display</a></li>
                    <li> <a target="iframe_a" href="./status.html">Status</a></li>
                </ul>
            </nav>
          </div> <!-- logo_text -->
        </div> <!-- logo -->
      </div> <!-- header -->
	  <div>
       <iframe src="current/current_density_z1_ten.php" name="iframe_a" width="100%" height="1200" style="border:none"></iframe>
      </div>
  

</body></html>
