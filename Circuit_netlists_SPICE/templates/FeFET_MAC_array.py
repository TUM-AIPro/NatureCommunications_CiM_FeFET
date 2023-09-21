##Author:Swetaki Chatterjee##


def get_inandstored(input,stored,capacitance):
    initial= f"""*** MAC Operation FeFET ****
    .hdl "code/ferrocap.va"
    .hdl "code/bsimimg.va"
    .include "code/modelcard.nmos"
    



    vdd supply  0 PWL(0 0, 0.0004u 0, 0.0005u 0.8, 35u 0.8)
    vclk clk 0 pulse (0 1 30u 0.01n 0.01n 0.25n 0.5n)


    **** INPUT *****
    *.param in={input}

    **** STORED *****
    *.param stored={stored}
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
        
        )
        
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
    

    
    C sl 0 c={capacitance}+32f //For bit-line capacitances
    Rcap sl 0 '100g*(TIME >= 0.0004u)'
    simulator lang=spectre



simulatorOptions options tnom=27 scalem=1.0 scale=1.0 rforce=1 maxnotes=5 maxwarns=5 digits=0 cols=80 

**MC montecarlo variations=process seed=1234 numruns=100
**{{
tranRun tran stop=0.020u outputstart=0.001u minstep=0.000000000000001p maxstep=10u writefinal="spectre.fc" annotate=status maxiters=100 autostop=no errpreset=conservative
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

.probe tran par'v(sl)'
.probe tran par'-i(vdd)'

.measure current9 find i(vdd) at 0.001u
.measure current6 find i(vdd) at 0.0035u
.measure current4 find i(vdd) at 0.006u
.measure current3 find i(vdd) at 0.0085u
.measure current2 find i(vdd) at 0.011u
.measure current1 find i(vdd) at 0.0135u
.measure tran sampling_v find v(sl) at 0.014u
.measure tran macro_power avg i(vdd) from 0.001u to 0.014u
*.measure tran i{out} find i(vdd) at {sampling_time}
.measure tran power avg i(vdd) from 30u to {sampling_time}
"""
