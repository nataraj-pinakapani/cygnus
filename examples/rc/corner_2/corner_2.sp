* Netlist: tb_rc.spice* Corner: {'lib': 'ss', 'RLOAD': 100.0}
.control
alter RLOAD 100.0
.endc
.lib /home/nataraj/projects/designmyic/cad/pdk/share/pdk/sky130B/libs.tech/ngspice/sky130.lib.spice ss
.include /home/nataraj/projects/designmyic/cad/cygnus/examples/rc/tb_rc.spice