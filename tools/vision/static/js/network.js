(function() {
    var container = document.getElementById('networkview');
    window.networkRefreshInt = 0;

    if (window.networkRefreshInt !== 0) {
        clearInterval(window.networkRefreshInt);
        window.networkRefreshInt = 0;
    }

    getNetwork();

    window.networkRefreshInt = setInterval(() => {
        getNetwork();
    }, 300000);

    function getNetwork() {
        fetch('/network').then((res) => {
            window.networkIds = window.networkIds || [];        
            var network = window.network;
            res.json().then((data) => {
                var options = {
                    nodes: {
                        shape: 'dot',
                        size: 30,
                        font: {
                            size: 22,
                            color: '#fffffff'
                        },
                        borderWidth: 1,
                        borderWidthSelected: 0,
                        color: {
                            highlight: {
                                border: 'orange',
                                background: 'white'
                            }
                        }
                    },
                    edges: {
                        width: 1,
                        length: 250,
                        arrows: {
                            to: {
                                enabled: true
                            }
                        },
                        color: 'white'
                    },
                    groups: {
                        dead: {color:{background:'gray'}, borderWidth:3},
                        linevast: {color:{background:'green'}, borderWidth:3},
                        blueangelhost: {color:{background:'blue'}, borderWidth:3},
                        twosync: {color:{background:'purple'}, borderWidth:3},
                        proxhost: {color:{background:'orange'}, borderWidth:3},
                        unknown: {color:{background:'brown'}, borderWidth:3},
                        undergroundprivate: {color:{background:'yellow'}, borderWidth:3},
                    },
                    physics:{
                        enabled: true,
                        barnesHut: {
                        gravitationalConstant: -5000,
                        centralGravity: 0.3,
                        springLength: 300,
                        springConstant: 0.15,
                        damping: 0.09,
                        avoidOverlap: 1
                        },
                        forceAtlas2Based: {
                        gravitationalConstant: -50,
                        centralGravity: 0.01,
                        springConstant: 0.08,
                        springLength: 300,
                        damping: 0.4,
                        avoidOverlap: 0
                        },
                        repulsion: {
                        centralGravity: 0.2,
                        springLength: 350,
                        springConstant: 0.15,
                        nodeDistance: 20,
                        damping: 0.09
                        },
                        hierarchicalRepulsion: {
                        centralGravity: 0.0,
                        springLength: 300,
                        springConstant: 0.01,
                        nodeDistance: 120,
                        damping: 0.09
                        },
                        maxVelocity: 50,
                        minVelocity: 0.1,
                        solver: 'barnesHut',
                        stabilization: {
                        enabled: true,
                        iterations: 1000,
                        updateInterval: 100,
                        onlyDynamicEdges: false,
                        fit: true
                        },
                        timestep: 0.5,
                        adaptiveTimestep: true
                    }
                    
                };	
        
                dataNodes = new vis.DataSet(data.nodes)
                dataEdges = new vis.DataSet(data.edges)
                            
                vData = {nodes: dataNodes, edges: dataEdges}

                for (var i = 0; i < data.nodes.length; i++) {
                    node = data.nodes[i];
                    window.networkIds.push(node.id);
                }

                if (network) {
                    network.destroy();
                }

                network = new vis.Network(container, vData, options);

                network.on('click', (params) => {
                    window.grapher.graphData(params.nodes[0]);
                });

                network.selectNodes([window.networkIds[0]]);
                window.grapher.graphData(network.getSelectedNodes()[0]);               
                document.body.addEventListener("click", function (e) {
                    if (e.target.className.split(" ")[0] === "mbtn") {
                        var key = e.target.getAttribute("data-monitor-key");
                        if (key === "info") {
                            var graph_container = document.getElementById('plebgraphs');
                            fetch('/node/'+network.getSelectedNodes()[0]+'/info').then((infoRes) => {
                                infoRes.json().then((data) => {
                                    alert(JSON.stringify(data));
                                });
                            });                             
                        } else {
                            window.grapher.graphData(network.getSelectedNodes()[0], key);
                        }
                    }
                });            
            });
        }); 
    }    
})();