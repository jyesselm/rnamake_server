from rnamake import motif_graph, util
import glob

#sc_files = glob.glob("sequence_opt_out_best/*.out")


f = open("default.out")
lines = f.readlines()
f.close()

for i, l in enumerate(lines):

    mg = motif_graph.MotifGraph(mg_str=lines[i])
    mg.to_pdb("test."+str(i)+".pdb", renumber=1, close_chain=1)