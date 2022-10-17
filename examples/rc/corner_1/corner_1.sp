* Netlist: tb_rc.spice* Corner: {'lib': 'ff', 'RLOAD': 10000.0}
.control
alter RLOAD 10000.0
.endc
.lib /home/nataraj/projects/designmyic/cad/pdk/share/pdk/sky130B/libs.tech/ngspice/sky130.lib.spice ff
.include /home/nataraj/projects/designmyic/cad/cygnus/examples/rc/tb_rc.spice