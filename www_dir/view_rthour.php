<html>

<?php # PHP Pre-Processing Block

 require "_functions.php";
 $array = array();
 foreach (file("stations.txt") as $line) {
	 list($key, $value) = explode(' ', $line, 2) + array(NULL, NULL);
	 if ($value !== NULL) {
		 $array[$key] = $value;
	 }
 }
 
 $prefix = trim($array["Prefix"]);

 ### ... ###
 $flDensity = ( isset($_REQUEST['density']) ? sanitize($_REQUEST['density'])  : 1    );
 $flZoom =    ( isset($_REQUEST['zoom']   ) ? sanitize($_REQUEST['zoom'])     : 0    );
 $strDate   = ( isset($_REQUEST['date']   ) ? sanitize($_REQUEST['date'])     : null );
 $strTime   = ( isset($_REQUEST['time']   ) ? sanitize($_REQUEST['time'])     : null );
 
 $strTitle = trim($array["Network"]) . " LMA: " . $strDate. " " . $strTime . " UTC";

/* End PHP Pre-Processing Block */ ?>

<head>
 <title><?php echo $strTitle ?></title>
 <link rel="stylesheet" type="text/css" href="layout_view_hour.css" />
 <link rel="stylesheet" type="text/css" href="style.css" />
</head>

<?php # PHP Processing Block

 $strYear  = substr($strDate, 0, 2);
 $strY2    = 2000 + $strYear;
 $strMonth = substr($strDate, 2, 2);
 $strDay   = substr($strDate, 4, 2);
 $strHour  = substr($strTime, 0, 2);

 $tmTime = strtotime("$strY2/$strMonth/$strDay $strHour:00");

 $prevHour = $tmTime - 3600;
 $prevDate = date("ymd",$prevHour);
 $prevTime = date("Hs",$prevHour);
 $urlShowPrev = "view_rthour.php?date=$prevDate&time=$prevTime&density=$flDensity&zoom=$flZoom";

 $nextHour = $tmTime + 3600;
 $nextDate = date("ymd",$nextHour);
 $nextTime = date("Hs",$nextHour);
 $urlShowNext = "view_rthour.php?date=$nextDate&time=$nextTime&density=$flDensity&zoom=$flZoom";

 $urlImgs = "img/$strYear/$strMonth/$strDay/$strHour";

 $flNewDensity = ($flDensity ? 0 : 1);
 $urlShow = "view_rthour.php?date=$strDate&time=$strTime&density=$flNewDensity&zoom=$flZoom";
 $strShow = ($flDensity == 0) ? "Densities" : "Points";

 $flNewZoom = ($flZoom ? 0 : 1);
 $urlZoom = "view_rthour.php?date=$strDate&time=$strTime&density=$flDensity&zoom=$flNewZoom";
 $strZoom = ($flZoom == 0) ? "In" : "Out";

if ( !$flDensity & !$flZoom ) {
	 $imgFullHour = $prefix . "_" . $strDate . "_" . $strHour . "0000_3600_z1_tim.full.png";
 } else if ( !$flDensity & $flZoom ) {
 	$imgFullHour = $prefix . "_" . $strDate . "_" . $strHour . "0000_3600_z2_tim.full.png";
 } else if ( $flDensity & !$flZoom ) {
	 $imgFullHour = $prefix . "_" . $strDate . "_" . $strHour . "0000_3600_z1_den.full.png";
 } else {
 	$imgFullHour = $prefix . "_" . $strDate . "_" . $strHour . "0000_3600_z2_den.full.png";
 }

 $htmlIntervalTable = "<table id='interval_table'>\n";

 for ($i=0;$i<=5;$i++) {
  $strMinute = sprintf("%02d", (10 * $i));
	if ( !$flDensity & !$flZoom ) {
 		$colorBar = "images/blank.gif";
  		$thmInterval = $prefix . "_"                                          . 
                 $strDate . "_"                                     . 
                 $strHour . $strMinute . "00_0600_z1_tim.thumb.png";
  		$imgInterval = $prefix . "_"                                          . 
                 $strDate . "_"                                     . 
                 $strHour . $strMinute . "00_0600_z1_tim.full.png";
	 } else if ( !$flDensity & $flZoom ) {
 		$colorBar = "images/blank.gif";
  		$thmInterval = $prefix . "_"                                          . 
                 $strDate . "_"                                     . 
                 $strHour . $strMinute . "00_0600_z2_tim.thumb.png";
  		$imgInterval = $prefix . "_"                                          . 
                 $strDate . "_"                                     . 
                 $strHour . $strMinute . "00_0600_z2_tim.full.png";
	 } else if ( $flDensity & !$flZoom ) {
 		$colorBar = "images/blank.gif";
  		$thmInterval = $prefix . "_"                                          . 
                 $strDate . "_"                                     . 
                 $strHour . $strMinute . "00_0600_z1_den.thumb.png";
  		$imgInterval = $prefix . "_"                                          . 
                 $strDate . "_"                                     . 
                 $strHour . $strMinute . "00_0600_z1_den.full.png";
	 } else {
 		$colorBar = "images/blank.gif";
  		$thmInterval = $prefix . "_"                                          . 
                 $strDate . "_"                                     . 
                 $strHour . $strMinute . "00_0600_z2_den.thumb.png";
  		$imgInterval = $prefix . "_"                                          . 
                 $strDate . "_"                                     . 
                 $strHour . $strMinute . "00_0600_z2_den.full.png";
	 }
  if ( file_exists("$urlImgs/$thmInterval") && file_exists("$urlImgs/$imgInterval") ) {
   $htmlIntervalTable .= <<<HTML_CONTENT
   <tr><td class="interval_time_stamp"> $strHour:$strMinute:00  </td></tr>
   <!--<tr><td class="interval_image"> <a target="_new" href="view_rt10min.php?date=$strDate&time=${strHour}${strMinute}00&density=$flDensity&zoom=$flZoom"><img border=2 src="$urlImgs/$thmInterval" /></a> </td></tr>-->
   <tr><td class="interval_image"> <a href="view_rt10min.php?date=$strDate&time=${strHour}${strMinute}00&density=$flDensity&zoom=$flZoom"><img border=2 src="$urlImgs/$thmInterval" /></a> </td></tr>

HTML_CONTENT;

  } else {

   $htmlIntervalTable .= <<<HTML_CONTENT
   <tr><td class="interval_time_stamp"> $strHour:$strMinute:00  </td></tr>
   <tr><td class="interval_image"> <img src="images/nodata.png" /> </td></tr>

HTML_CONTENT;
  }
 }

$htmlIntervalTable .= "  </table>";
 
/* End PHP Processing Block */ ?>

<body>

<!-- <div id="hour_container"> -->
 <div style="position: absolute; left: 0px; top: 0px">
  <h2 id="hour_title">Full Hour</h2>

  <div id="control_bar">
  <table width="700">
  <td width="25%" align=left>
   <a class="control_link" href="<?php echo $urlShowPrev ?>">[Previous Hour]</a>
  </td>
  <td width="30%">
   <a class="control_link" href="<?php echo $urlShow ?>">[Show <?php echo $strShow ?>]</a>
   </td>
  <td width="30%">
   <a class="control_link" href="<?php echo $urlZoom ?>">[Zoom <?php echo $strZoom ?>]</a>
   </td>
  <td width="15%" align=right>
   <a class="control_link" href="<?php echo $urlShowNext ?>">&nbsp&nbsp&nbsp[Next Hour]</a>
  </td>
   </table>
  </div>


  <img src="<?php echo "$urlImgs/$imgFullHour" ?>" />

  <br>

  <img src="<?php echo $colorBar ?>" vspace=20 >
  <br>

 </div>

<!-- <div id="interval_container"> -->
  <div style="position: absolute; left: 800px; top: 0px">
  <center>
   <h2 id="interval_title">10 Minute Intervals</h2>

   <?php echo $htmlIntervalTable ?>
  </center>
</div>

</body>
</html>
