.include tb_res_div.spice
.lib /home/nataraj/projects/designmyic/cad/pdk/share/pdk/sky130B/libs.tech/ngspice/sky130.lib.spice ff
.control
dc temp 0 100 1 VIN 0 3 0.5

write ff0.raw
.endc