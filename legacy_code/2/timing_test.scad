N = 20;
//1: 0
//2: 1
//3: 2
//4: 4
//5: 7
//6: 8
//7: 10
//8: 12
//9: 16
//10: 18s

//20: 46

for (i = [0:N-1]) {
translate([i*10*2, 0, 0])
  sphere(r=10, $fn=5);
  //cube([20, 20, 20], center = true);
}