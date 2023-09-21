##Author:Swetaki Chatterjee##


def get_inandstored(input,stored,capacitance):
    initial= f"""*** MAC Operation FeFET ****
    .hdl "/home/chattesi/FE-FDSOI/Final/code_fe/bsimimg.va"
    .hdl "/home/chattesi/FE-FDSOI/Final/code/ferrocap.va"
    .hdl "/home/chattesi/FE-FDSOI/Trial/code/bsimimg.va"
    .include "/scratch/net3/chattesi/Programmable_delay/SPICE_simulations/modelcard.nmos"
    .include "/scratch/net3/chattesi/DNN_FeFET/Sense_Amplifier/modelcard.pmos"
    *.include "/scratch/net3/chattesi/Ring_Oscillator/swetaki_netlist_parameterizer/templates/modelcard/modelcard1.pmos"


    .param v_sensing=0.3
    vdd supply  0 dc=0.8
    vclk clk 0 pulse (0 1.0 15n 0.01n 0.01n 15n 30n)
    Vsampling vthres 0 dc=v_sensing
    Vsampling1 vthres_b 0 dc=0.4
    **** INPUT *****
    *.param in={input}

    **** STORED *****
    *.param stored={stored}
    
    .subckt inv in out vd grond 

xp1 out in vd vd tp1 pmos1 W=40n L=20n
xn1 out in grond grond  tp2 nmos1 W=20n L=20n

.ends


.subckt sense_amplifier in1 in2 l0 r0 Vdd grnd clk

xm1 lb in1 tail grnd tm1 nmos1 W=133n L=20n
xm2 rb in2 tail grnd tm2 nmos1 W=133n L=20n
Xm3 l0 r0 lb grnd tm3 nmos1 W=133n L=20n
Xm4 r0 l0 rb grnd tm4 nmos1 W=133n L=20n

Xm5 l0 r0 Vdd Vdd tm5 pmos1 W=53n L=20n
Xm6 r0 l0 Vdd Vdd tm6 pmos1 W=53n L=20n

Xm7 tail clk grnd grnd tm7 nmos1 W=133n L=20n 


Xs1 lb clk Vdd Vdd ts1 pmos1 W=53n L=20n 
Xs2 rb clk Vdd Vdd ts2 pmos1 W=53n L=20n 
Xs3 l0 clk Vdd Vdd ts3 pmos1 W=53n L=20n 
Xs4 r0 clk Vdd Vdd ts4 pmos1 W=53n L=20n 

.ends


    """
    vth1=0.45
    vth2=0.90
    vth3=1.35
    vth4=2.8

    i=0
    length_of_array=len(stored)
    vsources=""
    wv_string=""
    circuit=""
    for inp in input:
        i=i+1
        if (inp==0):
         vsources+=f"""vfg{i} fg{i} 0 PWL(0 0,
        +0.0005u -2, 0.0025u -2, 
        +0.003u -2, 0.005u -2, 
        +0.0055u -1, 0.0075u -1,
        +0.008u -1, 0.0095u -1,
        +0.0100u -0.5, 0.011u -0.5,
        +0.0115u -0.5, 0.0125u -0.5,
        +0.013u 0, 0.015u 0,
        
        
        )
        
        """
        if (inp==1):
            vsources+=f"""vfg{i} fg{i} 0 PWL(0 0, 
        +0.0005u -0.5, 0.0025u -0.5, 
        +0.003u -0.5, 0.005u -0.5, 
        +0.0055u -0.5, 0.0075u -0.5,
        +0.008u -0.5, 0.0095u -0.5,
        +0.0100u {vth1}, 0.011u {vth1},
        +0.0115u {vth2}, 0.0125u {vth2},
        +0.013u {vth3}, 0.015u {vth3},
        
	  )
        
        """
        if (inp==2):
            vsources+=f"""vfg{i} fg{i} 0 PWL(0 0, 
        +0.0005u -0.5, 0.0025u -0.5, 
        +0.003u -0.5, 0.0050u -0.5, 
        +0.0055u {vth1}, 0.0080u {vth1},
        +0.0085u {vth2}, 0.010u {vth2},
        +0.0105u {vth2}, 0.011u {vth2},
        +0.0115u {vth3}, 0.013u {vth3}
        +0.0135u {vth3}, 0.015u {vth3}
        
        )
        
        """
        if (inp==3):
            vsources+=f"""vfg{i} fg{i} 0 PWL(0 0, 
        +0.00005u -0.5, 0.0009u -0.5, 
        +0.001u {vth1}, 0.0025u {vth1}
        +0.003u {vth1}, 0.0050u {vth1}, 
        +0.0055u {vth2}, 0.0075u {vth2},
        +0.008u {vth2}, 0.0095u {vth2},
        +0.0100u {vth3}, 0.0125u {vth3},
        +0.013u {vth3}, 0.015u {vth3}
        
        )measure power in spectre
        
        """
    i=0
    for sto in stored:
        i=i+1
        if (sto==0):
            wv_string+=f""".param wv{i}=-1.3
            .param st_v{i}=0
            .param bg_v{i}=0

        """
        if (sto==1):
            wv_string+=f""".param wv{i}=-0.6
            .param st_v{i}=0
            .param bg_v{i}=0

        """
        if (sto==2):
            wv_string+=f""".param wv{i}=-0.2
            .param st_v{i}=0
            .param bg_v{i}=0

        """
        if (sto==3):
            wv_string+=f""".param wv{i}=0.2
            .param st_v{i}=0
            .param bg_v{i}=0


        """

    subckt=f"""* --- FE-FDSOI Subcircuit ---
    simulator lang=spectre 
parameters del_vth=0
statistics {{
process {{ 
vary del_vth dist=gauss std=0.080 percent=no
}}
truncate tr=3.0
}}

simulator lang=spice
*.subckt nfefdsoi dr ga so bo
*Xnmos dr inga so bo aux nmos1 W=100n L=20n DELVTRAND=wv+del_vth
*Xfe   ga inga aux fecap time_step=1n dir_init=-1 Vo=5 m=3
*.ends

.model fecap pfecap """

    for i in range (1,length_of_array+1):
        circuit+=f"""

    X{i} int{i} fg{i} sl 0 nmos1 W=100n L=20n DELVTRAND=wv{i}+del_vth
    rs{i} supply int{i} r=5000k
    

"""
    end=f"""    
    

    
    C sl 0 c={capacitance}
    Xsa1 sli vthres1 out1 out1b supply 0 clk sense_amplifier 
    xinvr out1b y supply 0 inv

xinvl out1 x supply 0 inv


vincm1 sl sli dc=-0.4
vincm2 vthres vthres1 dc=-0.4
xlatch1 qoutb x 0 0 tlatc1 nmos1 W=100n L=20n 
xlatch2 qout y 0 0 tlatc2 nmos1 W=100n L=20n

xinv1 qoutb qout supply 0 inv
xinv2 qout qoutb supply 0 inv

Xsa2 sli1 vthres2 out2 out2b supply 0 clk sense_amplifier 
xinvr1 out2b y1 supply 0 inv
measure power in spectre
xinvl1 out2 x1 supply 0 inv


vincm3 sl sli1 dc=-0.4
vincm4 vthres_b vthres2 dc=-0.4
xlatch3 qout1b x1 0 0 tlatc3 nmos1 W=100n L=20n 
xlatch4 qout1 y1 0 0 tlatc4 nmos1 W=100n L=20n

xinv3 qout1b qout1 supply 0 inv
xinv4 qout1 qout1b supply 0 inv

    Rcap sl 0 '100g*(TIME >= 0.0004u)'
    simulator lang=spectre




simulatorOptions options tnom=27 scalem=1.0 scale=1.0 rforce=1 maxnotes=5 maxwarns=5 digits=0 cols=80 

**MC montecarlo variations=process seed=1234 numruns=100
**sw1 sweep param=v_sensing values=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
**{{
tranRun tran stop=0.023u outputstart=0.001u minstep=0.000000000000001p maxstep=10u writefinal="spectre.fc" annotate=status maxiters=100 autostop=no errpreset=conservative
**}}
modelParameter info what=models where=rawfile
element info what=inst where=rawfile
outputParameter info what=output where=rawfile
//designParamVals info what=parameters where=rawfile
//primitives info what=primitives where=rawfile
subckts info what=subckts  where=rawfile
"""
    final_string=initial+vsources+wv_string+subckt+circuit+end
    return final_string
def get_measure(out):
    if(out==9):
        sampling_time="0.001u"
    if(out==6):
        sampling_time="0.006u"
    if(out==4):
        sampling_time="0.006u"
    if(out==3):
        sampling_time="0.0085u"
    if(out==2):
        sampling_time="0.011u"
    if(out==1):
        sampling_time="0.0135u"
    if(out==0):
        sampling_time="0.0155u"


    return f"""
    *** MAC Operation FeFET ****
**** Measurement ****

simulator lang=spice


.measure current9 find i(vdd) at 0.001u
.measure current6 find i(vdd) at 0.0035u
.measure current4 find i(vdd) at 0.006u
.measure current3 find i(vdd) at 0.0085u
.measure current2 find i(vdd) at 0.011u
.measure current1 find i(vdd) at 0.0135u
.measure tran sampling_v find v(sl) at 0.014u
.measure tran macro_power integ i(vdd) from 0.001u to 0.023u
.measure tran out find v(qout) at 0.020u
*.measure tran i{out} find i(vdd) at {sampling_time}
.measure tran power avg i(vdd) from 30u to {sampling_time}
"""
