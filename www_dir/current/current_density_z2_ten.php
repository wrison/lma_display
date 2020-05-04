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

<META HTTP-EQUIV="refresh" content="10;URL=current_density_z2_ten.php">

<TITLE><?php echo $array["Network"] ?> LMA Current 10-Minute Density Plot</TITLE>

</HEAD>


<BODY>


<center>
	<h2><?php echo $array["Network"] ?> LMA Current 10-Minute Density Plot
</h2>
<h3>
10-Minute Density &nbsp
<a href=current_time_z2_ten.php>10-Minute Points</a> &nbsp
<a href=current_points_z2_two.php>2-Minute Points</a> &nbsp
<a href=current_time_z2_two.php>2-Minute Points (Color by Time)</a> &nbsp
<br>
<br>
<a href=current_density_z1_ten.php>Zoom 1</a> &nbsp 
Zoom 2 &nbsp 
<a href=current_density_z3_ten.php>Zoom 3</a> &nbsp 
</h3>
<br>
<IMG SRC = "current_0600_z2_den.png">
</center>

 </BODY>
 </HTML> 
