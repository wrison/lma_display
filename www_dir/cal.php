<?php
require "_config.inc.php";
require "_functions.php";
require "_class_calendar.php";

$calendar = new calendar;
if(!$_REQUEST['year2view']) {
	$_REQUEST['year2view'] = $calendar->get_currenttime();
}
$calendar->showall(sanitize($_REQUEST['year2view']), $blockwidth, $symbol);
?>
