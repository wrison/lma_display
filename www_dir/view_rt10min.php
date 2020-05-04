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
 $flDensity = ( isset($_REQUEST['density']) ?  sanitize($_REQUEST['density'])  : 1    );
 $flZoom =    ( isset($_REQUEST['zoom']   ) ? sanitize($_REQUEST['zoom'])      : 0    );
 $strDate   = ( isset($_REQUEST['date']   ) ? sanitize($_REQUEST['date'])      : null );
 $strTime   = ( isset($_REQUEST['time']   ) ? sanitize($_REQUEST['time'])      : null );
 
 $strTitle = trim($array["Network"]) . " LMA: " . $strDate. " " . $strTime . " UTC";

/* End PHP Pre-Processing Block */ ?>

<head>
 <title><?php echo "$strTitle" ?></title>
 <link rel="stylesheet" type="text/css" href="layout_view_hour.css" />
 <link rel="stylesheet" type="text/css" href="style.css" />
</head>

<?php # PHP Processing Block

 $strYear    = substr($strDate, 0, 2);
 $strY2    = 2000 + $strYear;
 $strMonth   = substr($strDate, 2, 2);
 $strDay     = substr($strDate, 4, 2);
 $strHour    = substr($strTime, 0, 2);
 $strMinute  = substr($strTime, 2, 2);

 $tmTime = strtotime("$strY2/$strMonth/$strDay $strHour:$strMinute");

 $prevPeriod = $tmTime - 600;
 $prevDate = date("ymd",$prevPeriod);
 $prevTime = date("Hi",$prevPeriod);
 $urlShowPrev = "view_rt10min.php?date=$prevDate&time=$prevTime&density=$flDensity&zoom=$flZoom";

 $nextPeriod = $tmTime + 600;
 $nextDate = date("ymd",$nextPeriod);
 $nextTime = date("Hi",$nextPeriod);
 $urlShowNext = "view_rt10min.php?date=$nextDate&time=$nextTime&density=$flDensity&zoom=$flZoom";

 $urlImgs = "img/$strYear/$strMonth/$strDay/$strHour";

 $flNewDensity = ($flDensity ? 0 : 1);
 $urlShow = "view_rt10min.php?date=$strDate&time=$strTime&density=$flNewDensity&zoom=$flZoom";
 $strShow = ($flDensity == 0) ? "Densities" : "Points";

 $flNewZoom = ($flZoom ? 0 : 1);
 $urlZoom = "view_rt10min.php?date=$strDate&time=$strTime&density=$flDensity&zoom=$flNewZoom";
 $strZoom = ($flZoom == 0) ? "In" : "Out";

if ( !$flDensity & !$flZoom ) {
	$img10min = $prefix . "_" . $strDate . "_" . $strHour . $strMinute . "00_0600_z1_tim.full.png";
 	$colorBar = "images/blank.gif";
 } else if ( !$flDensity & $flZoom ) {
 	$img10min = $prefix . "_" . $strDate . "_" . $strHour . $strMinute . "00_0600_z2_tim.full.png";
 	$colorBar = "images/blank.gif";
 } else if ( $flDensity & !$flZoom ) {
	$img10min = $prefix . "_" . $strDate . "_" . $strHour . $strMinute . "00_0600_z1_den.full.png";
 	$colorBar = "images/blank.gif";
 } else {
 	$img10min = $prefix . "_" . $strDate . "_" . $strHour . $strMinute . "00_0600_z2_den.full.png";
 	$colorBar = "images/blank.gif";
 }

/* End PHP Processing Block */ ?>

<body>

 <div id="hour_container">
  <h2 id="hour_title">10 Minute Plot</h2>

  <div id="control_bar">
  <table width="680">
  <td width="25%" align=left>
   <a class="control_link" href="<?php echo $urlShowPrev ?>">[Previous Interval]</a>
  </td>
  <td width="28%">
   <a class="control_link" href="<?php echo $urlShow ?>">[Show <?php echo $strShow ?>]</a>
   </td>
  <td width="28%">
   <a class="control_link" href="<?php echo $urlZoom ?>">[Zoom <?php echo $strZoom ?>]</a>
   </td>
  <td width="19%">
   <a class="control_link" href="<?php echo $urlShowNext ?>">[Next Interval]</a>
  </td>
   </table>

  </div>

  <img src="<?php echo "$urlImgs/$img10min" ?>" />

  <br>

  <img src="<?php echo $colorBar ?>" vspace=20 hspace=10>
 </div>

</body>
</html>
