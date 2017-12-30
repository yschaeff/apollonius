D = 2;

difference() {
  cube([200, 200, 20], center = true);
  translate([15, 15, 0])
    cube([200, 200, 40], center = true);
 translate([D, D, D])
  cube([200, 200, 20], center = true);
rotate([90, 0, 0])
  cylinder(r = 2, h = 300, center = true);
rotate([0, 90, 0])
  cylinder(r = 2, h = 300, center = true);

translate([-(100-20/2)-D/2, 100-10, 0])
cylinder(r = 1.5, h = 300, center = true);

translate([100-10, -(100-20/2)-D/2, 0])
cylinder(r = 1.5, h = 300, center = true);

translate([-(100-20/2)-D/2, -(100-20/2)-D/2, 0])
cylinder(r = 1.5, h = 300, center = true);

}
