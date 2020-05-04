<HTML>

<?php # PHP Pre-Processing Block

   $array = array();
   foreach (file("../stations.txt") as $line) {
  	 list($key, $value) = explode(' ', $line, 2) + array(NULL, NULL);
  	 if ($value !== NULL) {
  		 $array[$key] = $value;
  	 }
   }
 
/* End PHP Pre-Processing Block */ ?>


<HEAD>

<META HTTP-EQUIV="refresh" content="30;URL=current_anim_z3.php">

<TITLE><?php echo $array["Network"] ?> LMA Current 10-Minute Density Animation</TITLE>

</HEAD>


<BODY>


<center>
	<h2><?php echo $array["Network"] ?> LMA Current 10-Minute Density Animation
</h2>
<h3>
<a href=current_anim_z1.php>Zoom 1</a> &nbsp 
<a href=current_anim_z2.php>Zoom 2</a> &nbsp 
Zoom 3 &nbsp 
</h3>
<br>
<IMG SRC = "anim_z3.gif">
</center>

 </BODY>
 </HTML> 
