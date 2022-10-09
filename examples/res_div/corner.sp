.include tb_res_div.spice

*x1 GND OUT IN res_div
*VIN IN GND 1.8 AC 1
*RLOAD OUT GND 1

.lib /home/nataraj/projects/designmyic/cad/pdk/share/pdk/sky130B/libs.tech/ngspice/sky130.lib.spice tt
.control

write dc_tt.raw
.endc

