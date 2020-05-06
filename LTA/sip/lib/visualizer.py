#!/usr/bin/env python3

from graphviz import Digraph
import sys
from . import siplib
from . import ltasip

ltasip.Namespace.setPrefix('sip')

def visualize_sip(sip, path="sip.visualize", format="svg", view=False):
    if type(sip) == siplib.Sip:
        sip = sip._get_pyxb_sip(suppress_warning=True)

    linkstodataproduct = {}
    linkstoprocess = {}

    dot_wrapper = Digraph('cluster_wrapper')

    # ---
    # create legend
    dot_legend = Digraph('cluster_legend') # graphviz needs a label starting with cluster to render styles, oh boy...
    dot_legend.body.append('style=filled')
    dot_legend.body.append('bgcolor=lightgrey')
    dot_legend.body.append('label="Legend\n\n"')

    dot_legend.node('A',"Described Dataproduct",style="filled",fillcolor="cadetblue", shape="note")
    dot_legend.node('B',"Related Dataproduct",style="filled",fillcolor="cadetblue2", shape="note")
    dot_legend.node('C',"Observation", style="filled", fillcolor="gold",shape="octagon")
    dot_legend.node('D',"Pipeline/Process ",style="filled",fillcolor="chartreuse", shape="cds")
    dot_legend.node('E', "Unspec. Process", style="filled", fillcolor="orange", shape="hexagon")
    dot_legend.edge('A','B',color="invis")
    dot_legend.edge('B','C',color="invis")
    dot_legend.edge('C','D',color="invis")
    dot_legend.edge('D','E',color="invis")

    # ---
    # create the actual sip graph
    dot = Digraph('cluster_sip')
    dot.body.append('style=filled')
    dot.body.append('bgcolor=lightgrey')
    dot.body.append('label = "'+str(sip.project.projectCode+" - "+sip.project.projectDescription)+'\n\n"')

    # the dataproduct that is described by the sip
    data_out =  sip.dataProduct
    id_out = str(data_out.dataProductIdentifier.identifier)
    dot.node(id_out, id_out +": "+data_out.fileName,style="filled",fillcolor="cadetblue", shape="note")
    print("adding node for final dataproduct ", id_out)
    id_process = str(data_out.processIdentifier.identifier)
    # keep reference to originating pipeline run / observation:
    linkstodataproduct.setdefault(id_out,[]).append(id_process)

    # the input / intermediate dataproducts
    for data_in in sip.relatedDataProduct:
        id_in = str(data_in.dataProductIdentifier.identifier)
        dot.node(id_in, id_in +": "+data_in.fileName, style="filled", shape="note",fillcolor="cadetblue2")
        print("adding node for dataproduct ", id_in)
        id_process = str(data_in.processIdentifier.identifier)
        # keep reference to originating pipeline run / observation:
        linkstodataproduct.setdefault(id_in,[]).append(id_process)

    # the observations
    for obs in sip.observation:
        id_obs = str(obs.observationId.identifier)
        id_process = str(obs.processIdentifier.identifier)
        dot.node(id_process, id_process + ": "+ id_obs, style="filled", fillcolor="gold",shape="octagon")
        print("adding node for observation ", id_process)
        # no incoming data here, but register node as present:
        linkstoprocess.setdefault(id_process,[])

    # the data processing steps
    for pipe in sip.pipelineRun:
        id_pipe = str(pipe.processIdentifier.identifier)
        dot.node(id_pipe, id_pipe+" ", style="filled", fillcolor="chartreuse", shape="cds")
        print("adding node for pipelinerun ", id_pipe)
        # keep reference to input dataproducts:
        id_in = []
        for id in pipe.sourceData.content():
            id_in.append(str(id.identifier))
        linkstoprocess.setdefault(id_pipe,[]).append(id_in)

    # the data processing steps
    for unspec in sip.unspecifiedProcess:
        id_unspec = str(unspec.processIdentifier.identifier)
        dot.node(id_unspec, id_unspec, style="filled", fillcolor="orange", shape="hexagon")
        print("adding node for unspecified process ", id_unspec)
        # no incoming data here, but register node as present:
        linkstoprocess.setdefault(id_unspec,[])


    # todo: online processing
    # todo: parsets (?)

#    print linkstoprocess
#    print linkstodataproduct

    # add edges:
    for id in linkstodataproduct:
        for id_from in linkstodataproduct.get(id):
            if id_from in linkstoprocess:
                dot.edge(id_from, id)
                #print id_from,"->", id
            else:
                print("Error: The pipeline or observation that created dataproduct '"+ id + "' seems to be missing! -> ", id_from)

    for id in linkstoprocess:
        for ids_from in linkstoprocess.get(id):
            for id_from in ids_from:
                if id_from in linkstodataproduct:
                    dot.edge(id_from, id)
                    #print id_from,"->", id
                else:
                    print("Error: The input dataproduct for pipeline '"+ id +"' seems to be missing! -> ", id_from)


    # ----
    # render graph:
    dot_wrapper.subgraph(dot_legend)
    dot_wrapper.subgraph(dot)
    dot_wrapper = stylize(dot_wrapper)
    dot_wrapper.format = format
    print("writing rendering to", path)
    dot_wrapper.render(path, view=view)





def stylize(graph):
    styles = {
    'graph': {
        'fontname': 'Helvetica',
        'fontsize': '18',
        'fontcolor': 'grey8',
        'bgcolor': 'grey90',
        'rankdir': 'TB',
    },
    'nodes': {
        'fontname': 'Helvetica',
        'fontcolor': 'grey8',
        'color': 'grey8',
    },
    'edges': {
        'arrowhead': 'open',
        'fontname': 'Courier',
        'fontsize': '12',
        'fontcolor': 'grey8',
    }
    }

    graph.graph_attr.update(
        ('graph' in styles and styles['graph']) or {}
    )
    graph.node_attr.update(
        ('nodes' in styles and styles['nodes']) or {}
    )
    graph.edge_attr.update(
        ('edges' in styles and styles['edges']) or {}
    )
    return graph




def main(xmlpath):
    print("Reading xml from file", xmlpath)
    with open(xmlpath) as f:
        xml = f.read()
    sip = ltasip.CreateFromDocument(xml)
    path = xmlpath+".visualize"
    format = 'svg'
    visualize_sip(sip, path, format)


if __name__ == '__main__':
    main(sys.argv)