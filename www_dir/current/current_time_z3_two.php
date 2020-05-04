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

<META HTTP-EQUIV="refresh" content="10;URL=current_points_z3_two.php">

<TITLE><?php echo $array["Network"] ?> LMA Current 2-Minute Points Plot (Color by Time)</TITLE>

</HEAD>


<BODY>


<center>
	<h2><?php echo $array["Network"] ?> LMA Current 2-Minute Points Plot (Color by Time)
</h2>
<h3>
<a href=current_density_z3_ten.php>10-Minute Density</a> &nbsp
<a href=current_time_z3_ten.php>10-Minute Points</a> &nbsp
<a href=current_points_z3_two.php>2-Minute Points</a> &nbsp
2-Minute Points (Color by Time) &nbsp
<br>
<br>
<a href=current_time_z1_two.php>Zoom 1</a> &nbsp 
<a href=current_time_z2_two.php>Zoom 2</a> &nbsp 
Zoom 3 &nbsp 
</h3>
<br>
<IMG SRC = "current_0120_z3_tim.png">
</center>

 </BODY>
 </HTML> 
