<?php
function gettemplate($template,$ex="htm")
{
	global $templatefolder;
	return str_replace("\"","\\\"",implode("",file($templatefolder."/".$template.".".$ex)));
}

function dooutput($template)
{
	echo $template;
}
?>