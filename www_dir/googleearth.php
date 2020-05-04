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
<HEAD>

<title> <?php echo trim($array["Network"]) ?> LMA Google Earth Display </title

</HEAD>


<BODY>


<center>
    <h2><p style="font-family: helvetica, sans-serif; font-size: 64 pt;" >
	<a href=./geo_images/<?php echo trim($array["Network"])?>_realtime.kml> Oklahoma LMA Google Earth Display</a>
	</p>
	</h2>

</center>
	<p style="font-family: helvetica, sans-serif; font-size: 16 pt;" >
Download the file <a href=./geo_images/<?php echo trim($array["Network"])?>_realtime.kml> <?php echo trim($array["Network"])?>_realtime.kml</a> and open it in Google Earth to overlay the most recent <b>ten</b> minutes
of Oklahoma LMA data on Google Earth.  The image will automatically update one a minute. 
</p>

<p>
<br>


<center>
<h2><p style="font-family: helvetica, sans-serif; font-size: 64 pt;" >
Sample Image from April 22, 2020 </p></h2>

<a href=./geo_images/<?php echo trim($array["Network"])?>_realtime.kml> <IMG SRC = "./geo_images/google_earth_example.png"> </a>
</center>



