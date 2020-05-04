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

<META HTTP-EQUIV="refresh" content="10;URL=current_points_z2_two.php">

<TITLE><?php echo $array["Network"] ?> LMA Current 2-Minute Points Plot</TITLE>

</HEAD>


<BODY>


<center>
	<h2><?php echo $array["Network"] ?> LMA Current 2-Minute Points Plot
</h2>
<h3>
<a href=current_density_z2_ten.php>10-Minute Density</a> &nbsp
<a href=current_time_z2_ten.php>10-Minute Points</a> &nbsp
2-Minute Points &nbsp
<a href=current_time_z2_two.php>2-Minute Points (Color by Time)</a> &nbsp
<br>
<br>
<a href=current_points_z1_two.php>Zoom 1</a> &nbsp 
Zoom 2 &nbsp 
<a href=current_points_z3_two.php>Zoom 3</a> &nbsp 
</h3>
<br>
<IMG SRC = "current_0120_z2_pts.png">
</center>

 </BODY>
 </HTML> 
