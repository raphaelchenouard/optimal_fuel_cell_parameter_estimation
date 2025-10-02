import json

def generate_minibex(json_file,out_file):
    jfile = open(json_file,'r')
    json_string = jfile.read()
    jfile.close()
    data = json.loads(json_string)
    print(data)

    constants = """
    constants
    """
    constants += "\tN=" + str(len(data['I_exp'])) + ";\n"
    constants += "\tN_s=" + str(data['N_s']) + ";\n"
    constants += "\tA=" + str(data['A']) + ";\n"
    constants += "\tJ_max=" + str(data['J_max']) + ";\n"
    constants += "\tl=" + str(data['l']) + ";\n"
    if isinstance(data['T'],list):
        constants += "\tT[N]=" + str(data['T']).replace("[","(").replace("]",")").replace(",",";") + ";\n"
    else:
        constants += "\tT=" + str(data['T']) + ";\n"
    if isinstance(data['P_H_2'],list):
        constants += "\tP_H_2[N]=" + str(data['P_H_2']).replace("[","(").replace("]",")").replace(",",";") + ";\n"
    else:
        constants += "\tP_H_2=" + str(data['P_H_2']) + ";\n"
    if isinstance(data['P_O_2'],list):
        constants += "\tP_O_2[N]=" + str(data['P_O_2']).replace("[","(").replace("]",")").replace(",",";") + ";\n"
    else:
        constants += "\tP_O_2=" + str(data['P_O_2']) + ";\n"

    constants += "\tVm_stack[N]=" + str(data['V_exp']).replace("[","(").replace("]",")").replace(",",";") + ";\n"
    constants += "\tIm_stack[N]=" + str(data['I_exp']).replace("[","(").replace("]",")").replace(",",";") + ";\n"

    constants += """

    \tE_Nernst = 1.229-0.85e-3*(T-298.15)+4.3085e-5*T*(ln(P_H_2)+0.5*ln(P_O_2)); //open circuit voltage or reversible voltage per cell in V
    \tC_O_2 = P_O_2*exp(498/T)/5.08e6; // concentration of O2 in mol/cm3
    \tP_H_2_O = 10^(2.95e-2 * T - 9.18e-5 * T^2 + 1.44e-7 * T^3 - 2.18); // saturation pressure of water vapour

    """
    variables_sse = """
    variables
    \tksi_1 in [-1.1997,-0.8532];
    \tksi_2 in [1,5];
    \tksi_3 in [3.6,9.8];
    \tksi_4 in [-26,-9.54];
    \tlambda in [10,23];
    \tbeta in [0.0136,0.5];
    \tR_C in [.1,.8]; // connections resistance in mohm

    \tr[N] in [-oo,oo];
    """

    variables_sse_u = """
    variables
    \tksi_1 in [-1.1997,-0.8532];
    \tksi_2 in [1,5];
    \tksi_3 in [3.6,9.8];
    \tksi_4 in [-26,-9.54];
    \tR_C in [.1,.8]; // connections resistance in mohm
    \tlambda in [10,23];
    \tbeta in [0.0136,0.5];
    """

    variables_mae = """
    variables
    \tksi_1 in [-1.1997,-0.8532];
    \tksi_2 in [1,5];
    \tksi_3 in [3.6,9.8];
    \tksi_4 in [-26,-9.54];
    \tR_C in [.1,.8]; // connections resistance in mohm
    \tlambda in [10,23];
    \tbeta in [0.0136,0.5];

    \tmae[N] in [0,oo];
    """

    functions = """
    function V_act(I,ksi_1,ksi_2,ksi_3,ksi_4)
    \treturn -(ksi_1 + ksi_2*1e-3*T + ksi_3*1e-5*T*ln(C_O_2) + ksi_4*1e-5*T*ln(I))
    end

    function V_ohmic(I,R_C,lambda)
    \treturn I*(R_C*1e-3 + (l*(181.6*(1+0.03*I/A+0.062*(T/303)^2*(I/A)^2.5))
    \t\t / ((lambda-0.634-3*I/A)*exp(4.18*(T-303)/T)))/A
    \t)
    end

    function V_con(I,beta)
    \treturn -beta*ln(1-(I/A)/J_max)
    end

    function fV(I,R_C,ksi_1,ksi_2,ksi_3,ksi_4,lambda,beta)
    \treturn N_s * (
    \t\tE_Nernst - V_act(I,ksi_1,ksi_2,ksi_3,ksi_4) - V_ohmic(I,R_C,lambda) - V_con(I,beta)
    \t)
    end
    """

    sse_obj_ctr = """
    Minimize sum(i=0:N-1,(r[i])^2)

    Constraints
    \tfor i=0:N-1;
    \t\tr[i] = Vm_stack[i]-fV(Im_stack[i],R_C,ksi_1,ksi_2,ksi_3,ksi_4,lambda,beta);
    \tend;
    End
    """

    mae_obj_ctr = """
    Minimize sum(i=0:N-1,mae[i])/N

    Constraints
    for i=0:N-1;
        mae[i] >= Vm_stack[i] - fV(Im_stack[i],R_C,ksi_1,ksi_2,ksi_3,ksi_4,lambda,beta);
        -mae[i] <= Vm_stack[i] - fV(Im_stack[i],R_C,ksi_1,ksi_2,ksi_3,ksi_4,lambda,beta);
    end;
    End
    """

    print('Writing ' + out_file + '_sse.mbx ...')
    sse_file = open(out_file+'_sse.mbx','w')
    sse_file.write(constants+variables_sse+functions+sse_obj_ctr)
    sse_file.close()


    print('Writing ' + out_file + '_mae.mbx ...')
    mae_file = open(out_file+'_mae.mbx','w')
    mae_file.write(constants+variables_mae+functions+mae_obj_ctr)
    mae_file.close()


import sys

if __name__ == '__main__':
    json_file="../data/H-12.json"
    out_file='pemfc'

    if len(sys.argv)==2:
        json_file = sys.argv[1]
    elif len(sys.argv)==3:
        json_file = sys.argv[1]
        out_file = sys.argv[2]

    generate_minibex(json_file,out_file)
