<?php

/*/^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^/*/
/*/^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^/*/
/*/ Viet Calendar v1.0.050103         /*/
/*/ Copyright (C) 2003 Deathly Smile                /*/
/*/ If you have any comments about Viet Calendar,    /*/
/*/   please send email to dsmile@softhome.net   /*/
/*/ If you use this scripts for any purposes,     /*/
/*/please keep the line "Powered by VietPHP" in your html.   /*/
/*/^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^/*/
/*/ For more free PHP scripts,         /*/
/*/                visit Viet Calendar's Homepage at   /*/
/*/    http://www.vietphp.com      /*/
/*/^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^/*/
/*/^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^/*/

class calendar
{
 var $calendars;
 var $fullcalendar;
 var $daynamesrow;
 var $dayscolor;
 var $background;

 function get_currenttime()
 {
  global $timeoffset, $realtime, $currentday, $currentmonth,$currentyear;
  
  $realtime = time() + 3600*$timeoffset;

  $currentday   = date(d, $realtime);
  $currentmonth = date(m, $realtime);
  $currentyear  = date(Y, $realtime);

  return $currentyear;
 }

 function get_daycolor($num)
 {
  global $saturdaycolor, $sundaycolor, $normaldaycolor;
 
  if($num % 7 == 0)
   $this->dayscolor = $sundaycolor;
  elseif($num % 7 == 6)
   $this->dayscolor = $saturdaycolor;
  else
   $this->dayscolor = $normaldaycolor;

  return $this->dayscolor;
 }

 function get_background($month, $day, $year)
 {
  global $realtime, $currentday, $currentmonth,$currentyear, $imagesdir, $cellbackgroundcolor;

  $this->get_currenttime();
  if(mktime(0, 0, 0, $month, $day, $year) > $realtime)
   $this->background = "class=\"smallgrey\"";
  else   
   $this->background = "class=\"smallgrey\"";
  
  return $this->background;
 }

 function dataexists($datestring)
 {
  $month = substr($datestring, 2, 2);
  $day   = substr($datestring, 4, 2);
  $year  = substr($datestring, 0, 2);
  
  $ret = file_exists("./img/$year/$month/$day");
//  $ret =         file_exists("./img/$year/$month/$day/LYLOUT_" . $datestring . "_000000_3600.600.png");
//  $ret = $ret || file_exists("./img/$year/$month/$day/LYLOUT_" . $datestring . "_150000_3600.600.png");
//  $ret = $ret || file_exists("./img/$year/$month/$day/LYLOUT_" . $datestring . "_000000_3600.450.600.png");
//  $ret = $ret || file_exists("./img/$year/$month/$day/LYLOUT_" . $datestring . "_150000_3600.450.600.png");

  return $ret;
 }

 function create_daynames()
 {
  global $startday, $daynames, $imagesdir, $cellbackgroundcolor;

  if($startday != 0)
   $startday = -1;

  $this->daynamesrow = "";

  for($i=0;$i<=6;$i++)
  {
   $daycolor = $this->get_daycolor($i + $startday + 1);
   $day = $daynames[$i + $startday];
   
   if(!$day)
    $day = $daynames[$i + $startday + 7];

   $day = "<b>".$day."</b>";

   $background = "class=\"smallgrey\" bgcolor=\"$cellbackgroundcolor\" background=\"$imagesdir/boxbg.gif\"";
   $this->daynamesrow .= "<td align=\"center\" $background><font color=\"$daycolor\">$day</font></td>";

  }

  return $this->daynamesrow;
 }

 function create_singlemonth($month, $year, $blockwidth, $symbol=1)
 {
  global $startday, $monthnames, $imagesdir, $headercolor, $bordercolor, $cellbackgroundcolor, $cellbackgroundcolorlight, $monthheadercolor;
  
  $gettime = mktime(0, 0, 0, $month, 1, $year);
  $monthname = $monthnames[$month-1];
  $totaldays = date("t", $gettime);
  $startweek = getdate($gettime);
  
  if($startday != 0)
   $startday = -1;

  $colspan = $startweek[wday] - 1 - $startday;
  
  if($colspan <= -1)
   $colspan = 6;
  
  if($colspan != 0) {
   eval ("\$calendar = \"".gettemplate("calendar_firstrowbit")."\";");
  }

  for($day=1;$day<=$totaldays;$day++) {

   if(($day + $colspan) % 7 == 1) {
    $calendar =  $calendar."\n</tr>\n<tr>\n";
   }

   if($symbol)
    $background = $this->get_background($month, $day, $year);
   else
    eval ("\$background = \"".gettemplate("calendar_ndaybg")."\";");
   
   $datestring= sprintf("%02d%02d%02d",($year-2000),$month,$day);
   $daycolor = "black";
   
   if($this->dataexists($datestring)) {
    $calendar .= "<td width=\"10%\" align=\"center\" $background bgcolor=\"$cellbackgroundcolorlight\"" .
     "background=\"$imagesdir/boxbg.gif\"><font color=\"$daycolor\"><a href=\"rt.php?date=$datestring\">[$day]</a></font></td>";
   } else {
    $calendar .= "<td width=\"10%\" align=\"center\" $background bgcolor=\"$cellbackgroundcolor\">" .
     "<font color=\"$daycolor\">$day</font></td>";
   }
  }
  
  $colspan = ($totaldays + $colspan) % 7;
  if($colspan != 0) {
   $colspan = 7 - $colspan;
   eval ("\$calendar .= \"".gettemplate("calendar_lastrowbit")."\";");
  }

  $daynamerow = $this->create_daynames();

  eval ("\$this->calendars = \"".gettemplate("calendar_monthindex")."\";");
  return $this->calendars;
 }

 function create_fullyear($year, $blockwidth, $symbol)
 {
  global $blockperrow, $currentyear, $imagesdir;
  
  $prevyear = $year-1;
  $nextyear = $year+1;
  $this->fullcalendar = "<tr>\n";

  for($i=1;$i<=12;$i++) {
   $this->fullcalendar .= "<td valign='top' align='center'>".$this->create_singlemonth($i,$year, $blockwidth, $symbol)."</td>\n";
   if($i%$blockperrow == 0) $this->fullcalendar = $this->fullcalendar."\n</tr>\n<tr>\n";
  }

  $fullcalendar = $this->fullcalendar;

  eval("dooutput(\"".gettemplate("calendar_index")."\");");
 }

 function create_currentmonth($blockwidth, $symbol=1)
 {
  global $currentmonth,$currentyear;
  
  $this->get_currenttime();
  
  return $this->create_singlemonth($currentmonth, $currentyear, $blockwidth, $symbol);
 }

 function showall($year, $blockwidth, $symbol)
 {
  return $this->create_fullyear($year, $blockwidth, $symbol);
 }

}
?>
