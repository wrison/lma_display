<!DOCTYPE html>
<html>

<?php # PHP Pre-Processing Block

 require "_functions.php";
 date_default_timezone_set('UTC');

 $today = date('ymd', time());

 $myYear    = substr($today, 0, 2);
 $myY2    = 2000 + $myYear;
 $myMonth   = substr($today, 2, 2);
 $myDay     = substr($today, 4, 2);
 $myTime = strtotime("$myY2/$myMonth/$myDay");
 $myYesterday = $myTime - 3600*24;
 $startDate = date("ymd",$myYesterday);

 $strDate   = ( isset($_REQUEST['date']   ) ? sanitize($_REQUEST['date'])      : $startDate );
 $strStation   = ( isset($_REQUEST['station']   ) ? sanitize($_REQUEST['station'],false)      : 'A' );
 $strImage = "./plots/$strStation/T$strStation$strDate.png";


 $strYear    = substr($strDate, 0, 2);
 $strY2    = 2000 + $strYear;
 $strMonth   = substr($strDate, 2, 2);
 $strDay     = substr($strDate, 4, 2);

 $tmTime = strtotime("$strY2/$strMonth/$strDay");
 $tmYesterday = $tmTime - 3600*24;
 $tmTomorrow  = $tmTime + 3600*24;
 $prevDate = date("ymd",$tmYesterday);
 $nextDate = date("ymd",$tmTomorrow);
 $urlShowNext = "stat_plots.php?date=$nextDate&station=$strStation";
 $urlShowPrev = "stat_plots.php?date=$prevDate&station=$strStation";

 $array = array();
 foreach (file("stations.txt") as $line) {
	 list($key, $value) = explode(' ', $line, 2) + array(NULL, NULL);
	 if ($value !== NULL) {
		 $array[$key] = $value;
	 }
 }

/* End PHP Pre-Processing Block */ ?>

<head>
 <title><?php echo $array["Network"]." LMA Plots"  ?></title>
<style>
#header {
    background-color:black;
    color:white;
    text-align:center;
    padding:5px;
}
#nav {
    line-height:20px;
    background-color:#dddddd;
    height:1200px;
    width:250px;
    float:left;
    padding:5px;	      
}
#files {
    line-height:20px;
    background-color:#eeeeee;
    height:1200px;
    width:150px;
    float:left;
    padding:5px;	      
}
#section {
    width:350px;
    float:left;
    padding:10px;	 	 
}
</style>
</head>
<body>

<div id="header">
 <h1><?php echo $array["Network"] . " LMA Status Plots" ?></h1>
</div>

<div id="nav">
<h3> Station <?php echo $strStation ?> </h3>

<table class="sortable">
  <tbody>
      <?php
		$dirlist = glob("plots/[A-Z]");
		
		foreach ($dirlist as $item) {
			$s = substr($item,6,1);
	  		$myURL2 = "stat_plots.php?date=$strDate&station=$s";
			print ("
				<tr>
            <td><a href=$myURL2>$s $array[$s]</a></td>
				</tr>\n");
		}
	?>
  </tbody>
</table>
</div>

<div id="files">
<h3> File </h3>
    <table class="sortable">
      <tbody>
      <?php
        // Opens directory
        $myDirectory=opendir("./plots/$strStation");
        
        // Gets each entry
        while($entryName=readdir($myDirectory)) {
          $dirArray[]=$entryName;
        }
        
        // Closes directory
        closedir($myDirectory);
        
        // Counts elements in array
        $indexCount=count($dirArray);
        
        // Sorts files
        rsort($dirArray);
        
        // Loops through the array of files
        for($index=0; $index < $indexCount; $index++) {
        
          // Allows ./?hidden to show hidden files
          if($_SERVER['QUERY_STRING']=="hidden")
          {$hide="";
          $ahref="./";
          $atext="Hide";}
          else
          {$hide=".";
          $ahref="./?hidden";
          $atext="Show";}
          if(substr("$dirArray[$index]", 0, 1) != $hide) {
          
          // Gets File Names
          $name=$dirArray[$index];
          $namehref=$dirArray[$index];
	  $myStation = substr($name,1,1);
	  $myDate = substr($name,2,6);
	  $myURL = "stat_plots.php?date=$myDate&station=$myStation";

                    
          // Print 'em
          print("
          <tr class='$class'>
            <td><a href=$myURL>$name</a></td>
          </tr>");
          }
        }
      ?>
      </tbody>
    </table>

</div>


<div id="section">
  <div id="control_bar">
  <table width="785">
  <td width="50%" align=left>
   <a class="control_link" href="<?php echo $urlShowPrev ?>">[Previous Day]</a>
  </td>
  <td width="50%" align=right>
   <a class="control_link" href="<?php echo $urlShowNext ?>">[Next Day]</a>
  </td>
   </table>

  </div>


<p>
<?php
    if (file_exists($strImage))
    {	
	print ("<IMG SRC = $strImage > <br>
               ");
    } else {	
	print ("<IMG SRC = plots/no_data.png> <br>
               ");
    }
?>

</p>
</div>

</body>
</html>


