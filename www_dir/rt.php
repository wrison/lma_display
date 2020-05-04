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
 
   $strDate   = isset($_REQUEST['date']   ) ? sanitize($_REQUEST['date'])    : null;
   $year  = substr($strDate, 0, 2);
   $strTitle = $array["Network"] . " LMA: 20$year";

   $prefix = trim($array["Prefix"]);

/* End PHP Pre-Processing Block */ ?>

<head>
 <title><?php echo "$strTitle" ?></title>
 <link rel="stylesheet" type="text/css" href="style.css" />
<head>

<?php # PHP Processing Block

   // Get passed variables
   $strDate   = isset($_REQUEST['date']   ) ? sanitize($_REQUEST['date'])    : null;
   $flDensity = isset($_REQUEST['density']) ? sanitize($_REQUEST['density']) : 1; // Use density=1 by default
   $flZoom = isset($_REQUEST['zoom']) ? sanitize($_REQUEST['zoom']) : 0; // Use zoom=0 by default

   // Validate Input
   // Date:


   // Density:
   $flDensity    = ($flDensity) ? TRUE  : FALSE;
   $flNewDensity = ($flDensity) ? FALSE : TRUE;


   // Zoom
   $flZoom    = ($flZoom) ? TRUE  : FALSE;
   $flNewZoom = ($flZoom) ? FALSE : TRUE;

   // Format Date information     
   // substr(<string>, <start>, [len]);
   $year  = substr($strDate, 0, 2);
   $month = substr($strDate, 2, 2);
   $day   = substr($strDate, 4, 2);

   $tmDate = strtotime("20$year-$month-$day");
   $strFormattedDate = date("F jS, Y", $tmDate);

   $nextDay = date("ymd",strtotime("1 day",$tmDate));
   $prevDay = date("ymd",strtotime("1 day ago",$tmDate));

   // Toggle 'Show' text
   if ($flDensity) {
    $strShow = 'Points';
   } else {
    $strShow = 'Densities';
   }

   // Toggle 'Zoom' text
   if ($flZoom) {
    $strZoom = 'Out';
   } else {
    $strZoom = 'In';
   }


   // Generate Table Content
   $htmlThumbnails = "";
   for($i=0;$i<=3;$i++) {

    $htmlThumbnails .= "\n     <tr>";

    // Thumbnail Title Row:
    for($j=0;$j<=5;$j++) {
     
     $hour = sprintf("%02d",$j+$i*6);
     $htmlThumbnails .= <<<HTML_content

      <td class="time_stamp">
       ${hour}:00 - ${hour}:59
      </td>

HTML_content;

    }

    $htmlThumbnails .= "     </tr>\n\n     <tr>";

    // Thumbnail Image Row:
    for ($j=0 ; $j<=5 ; $j++) {

     // Needs to be updated for new dir struct!

     // substr(<string>, <start>, [len]);
     $month = substr($strDate, 2, 2);
     $day   = substr($strDate, 4, 2);
     $year  = substr($strDate, 0, 2);
     
     $hour = sprintf("%02d",$j+$i*6);
     $thmData = "img/$year/$month/$day/$hour/$prefix" . "_"        . 
                 $strDate . "_"                                    . 
                 $hour . "0000_3600"                               .
                 (  $flDensity &  $flZoom ? "_z2_den.thumb" : "")  .
                 (  $flDensity & !$flZoom ? "_z1_den.thumb" : "")  .
                 ( !$flDensity &  $flZoom ? "_z2_tim.thumb" : "")  .
                 ( !$flDensity & !$flZoom ? "_z1_tim.thumb" : "")  .
                 ".png";


     $imgData = "img/$year/$month/$day/$hour/$prefix" . "_"        . 
                 $strDate . "_"                                    . 
                 $hour . "0000_3600"                               .
                 (  $flDensity &  $flZoom ? "_z2_den.full" : "")   .
                 (  $flDensity & !$flZoom ? "_z1_den.full" : "")   .
                 ( !$flDensity &  $flZoom ? "_z2_tim.full" : "")   .
                 ( !$flDensity & !$flZoom ? "_z1_tim.full" : "")   .
                 ".png";

     if ( file_exists($thmData) && file_exists($imgData) ) {

      $htmlThumbnails .= <<<HTML_content

      <td align="center">
       <!--<a href="view_rthour.php?date=$year$month$day&time=${hour}00&density=$flDensity&zoom=$flZoom" target="_new"> -->
       <a href="view_rthour.php?date=$year$month$day&time=${hour}00&density=$flDensity&zoom=$flZoom">
        <img width="100" height="100" border="0" src="$thmData">
       </a>
      </td>

HTML_content;

     } else {

      $htmlThumbnails .= "\n      <td align=\"center\"><img src=\"images/nodata.png\"></td>\n";

#      DEBUGGING OUTPUT
#      $htmlThumbnails .= "\n      <td align=\"center\"><img alt=\"$strDate : $year $month $day\"src=\"images/nodata.png\"></td>\n";

     }

    }

    $htmlThumbnails .= "     </tr>\n";

   }

/* END PHP Processing Block */ ?>

<body>
 <center>
  <table border="0" cellpadding="2" width="225" bgcolor="#cccccc" cellspacing="1" align="center">

   <tr>
    <td width="10%" class="header" colspan="1">
     <a href="rt.php?<?php echo "date=$strDate&density=$flNewDensity&zoom-$flZoom" ?>"><?php echo "Show $strShow" ?></a>
    </td>

    <td width="100%" class="header" colspan="4">
     <?php echo "$strFormattedDate" ?>
    </td>
    <td width="10%" class="header" colspan="1">
     <a href="rt.php?<?php echo "date=$strDate&zoom=$flNewZoom&density=$flDensity" ?>"><?php echo "Zoom $strZoom" ?></a>
    </td>


   </tr>

   <!-- GENERATED SEGMENT: START -->
   <?php # Enter Pre-Generated Thumbnail HTML Data
      echo $htmlThumbnails;
   ?>
   <!-- GENERATED SEGMENT: END   -->

   <tr>

    <td width="100%" class="footer" colspan="1">
     <a href="rt.php?<?php echo "date=$prevDay&density=$flDensity&zoom=$flZoom" ?>"><?php echo "Previous Day" ?></a>
    </td>

    <td width="100%" class="footer" colspan="4">
     <a href="cal.php">[&lt;&lt;back]</a>
    </td>

    <td width="100%" class="footer" colspan="1">
     <a href="rt.php?<?php echo "date=$nextDay&density=$flDensity&zoom=$flZoom" ?>"><?php echo "Next Day" ?></a>
    </td>

   </tr>

  </table>
 </center>

</body>
</html>
