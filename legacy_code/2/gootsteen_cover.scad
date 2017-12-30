difference() {
cube([15, 44, 2], center=true);
translate([0, 34/2, 0])
  cylinder(r=1.5, h = 20, center=true, $fn=16);
translate([0, -34/2, 0])
  cylinder(r=1.5, h = 20, center=true, $fn=16);
}



translate([0, 0, (5+2)/2])
  cylinder(r=7.5, h = 5, center=true, $fn=64);
  
