(function() {
    window.grapher = window.grapher || {};
    var grapher = window.grapher;

    grapher.lastGraph = undefined;
    grapher.units = {
        'MB_balance' : 'MBs',
        'downloaded' : 'MBs',
        'uploaded' : 'MBs',
        'matchmakers' : 'peers'
    };
    grapher.defaultSelection = 'uploaded';
    grapher.selected = grapher.defaultSelection;

    grapher.refreshInt = 0;

    grapher.graphData = function(node, key) {
        if (typeof key === 'undefined') {
            key = grapher.selected;
        } else {
            grapher.selected = key;
        }

        if (grapher.refreshInt !== 0) {
            clearInterval(grapher.refreshInt);
            grapher.refreshInt = 0;
        }

        grapher.getDataAndGraph(node, key);

        grapher.refreshInt = setInterval(() => {            
            grapher.getDataAndGraph(node, key);
        }, 300000);   
    };

    grapher.getDataAndGraph = function(node, key) {
        fetch('/node/'+node+'/'+key).then((nodeRes) => {
            nodeRes.json().then((nodeData) => {
                try {
                    window.grapher.graph(key, nodeData)
                } catch (err) {
                    grapher.clear();
                }
            });
        });
    }

    grapher.clear = function() {
        if (grapher.lastGraph) {
            grapher.lastGraph.destroy();
        }        
    }

    grapher.graph = function(key, data) {
        var graph_container = document.getElementById('plebgraphs');
        var dataset = new vis.DataSet(data);
        var options = {
            start: data[0].x,
            end: data[data.length-1].x,         
            dataAxis: {
                showMinorLabels: false,
                left: {
                    title: {
                        text: key + ' (' + grapher.units[key] + ')'
                    },
                    range: {
                        min: 0,
                        max: data[data.length-1].y * 1.5 
                    }
                }
            },
            drawPoints: true,
            shaded: {
                orientation: 'zero' // top, bottom
            },        
            autoResize: true,
            moveable: false,
            graphHeight: '395px',
        }

        grapher.clear()

        var groups = new vis.DataSet();
        groups.add({
            id: 0,
            content: 'namess',
            className: 'custom-style1',
            options: {
                drawPoints: {
                    style: 'square' // square, circle
                },
                shaded: {
                    orientation: 'bottom' // top, bottom
                }
            }});        

        grapher.lastGraph = new vis.Graph2d(graph_container, dataset, groups, options);          
    }
}) ();
