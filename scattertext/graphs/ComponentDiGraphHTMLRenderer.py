import json

class GraphRenderer(object):
    def get_graph(self):
        raise NotImplementedError()

    def get_javascript(self):
        raise NotImplementedError

class ComponentDiGraphHTMLRenderer(GraphRenderer):
    def __init__(self,
                 component_graph,
                 width=1000,
                 height=1000,
                 enable_pan_and_zoom=True,
                 engine='dot'):
        self.component_graph = component_graph
        self.width = width
        self.height = height
        self.enable_pan_and_zoom = enable_pan_and_zoom
        self.engine = engine

    def get_graph(self):

        selected_components = self.component_graph.get_components_at_least_size(0)
        all_svg = ''
        for i, component in enumerate(selected_components):
            dot_str = self.component_graph.get_dot(component)
            raw_svg = self.get_svg(dot_str)
            lines = raw_svg.split('\n')
            lines[9] = lines[9].replace('graph0', 'graph%s' % (component))
            lines[6] = ('<svg easypz width="{width}pt" height="{height}pt" id="svg{component}"'
                        + ' style="display: none" class="dotgraph"').format(
                width=self.width, height=self.height, component=component
            )
            for line in lines[6:]:
                if line.startswith('<!--') or line.endswith('-->'):
                    continue
                all_svg += line + '\n'
        return all_svg

    def get_svg(self, dot_str):
        import graphviz as gv

        return gv.Source(dot_str, format='svg', engine=self.engine).pipe().decode('utf-8')

    def get_javascript(self):
        return '''
        name_to_component = %s;
        
        name_to_coord = {}; // term -> {x, y, svg} 
        origViewBox = {}; // svgid -> viewbox
        
        Array.prototype.forEach.call(
            document.querySelectorAll(".dotgraph"),
            function(svg) {
                origViewBox[svg.id] = svg.getAttribute('viewBox');
                
                Array.prototype.forEach.call(
                    svg.getElementsByTagName('text'), 
                    function(text) {
                        name_to_coord[text.textContent] = {
                            "x": text.getAttribute("x"), 
                            "y": text.getAttribute("y"), 
                            "svg": svg.id
                        };
                    }
                )
            }
        ) 
        
        panZoomInstance = null;
        
        
        function zoomToName(name) {
        
            //panZoomInstance.reset();
                        
                        
            console.log("ZOOMING TO "); console.log(name);
            panZoomInstance.fit();
            panZoomInstance.center(); 
            
            var pzSizes = panZoomInstance.getSizes();
            var centerX = name_to_coord[name].x;
            var centerY = -name_to_coord[name].y;
            var newX = centerX*pzSizes["width"]/pzSizes["viewBox"]["width"];
            var newY = centerY*pzSizes["height"]/pzSizes["viewBox"]["height"];
            
            //var zoomRatio = 1/(pzSizes["width"]/pzSizes["viewBox"]["width"]);
            console.log('zr '.concat(name, ' ', pzSizes, ' ', centerX, ' ', centerY, ' ', newX, ' ', newY));       
            panZoomInstance.zoomAtPointBy(5, {'x':newX, 'y':newY});
        }
        
        function panToName(name) {
            var x = name_to_coord[name].x; 
            var y = panZoomInstance.getSizes().viewBox.height + Number.parseInt(name_to_coord[name].y); 
            panZoomInstance.reset() 
            panZoomInstance.zoom(1/panZoomInstance.getSizes().realZoom, true)
            panZoomInstance.pan({x:0,y:0});
            var realZoom = panZoomInstance.getSizes().realZoom; 
            var destX = -((x * realZoom) - (panZoomInstance.getSizes().width/2));
            var destY = -((y * realZoom) - (panZoomInstance.getSizes().height/2));
            panZoomInstance.pan({'x':0,'y':0}); 
            panZoomInstance.pan({'x': destX, 'y': destY})
        }
            
        
        function showTermGraph(term) {
            var nodeName = 'svg' + name_to_component[term];
            document.getElementById(nodeName).style.display='block'; 
            %s
            panToName(term);
        }

        Array.from(document.querySelectorAll('.node')).map(
            function (node) {
                node.addEventListener('mouseenter', mouseEnterNode);
                node.addEventListener('mouseleave', mouseLeaveNode);
                node.addEventListener('click', clickNode);
            }
        )
        
        function clickNode() {
            document.querySelectorAll(".dotgraph")
                .forEach(node => node.style.display = 'none');

            var term = Array.prototype.filter
                .call(this.children, (x => x.tagName === "text"))[0].textContent;

            plotInterface.handleSearchTerm(term, true);
        }

        function mouseEnterNode(event) {
            var term = Array.prototype.filter.call(this.children, (x => x.tagName === "text"))[0].textContent;
            plotInterface.showTooltipSimple(term);
            this.style.fill="red";
        }

        function mouseLeaveNode() {
            plotInterface.tooltip.transition().style('opacity', 0)
            this.style.fill="black";
        }''' % (json.dumps(self.component_graph.get_node_to_component_dict()),
                self._get_pan_and_zoom_js())

    def _get_pan_and_zoom_js(self):
        if self.enable_pan_and_zoom:
            return '''
                panZoomInstance = svgPanZoom('#' + nodeName, {
                    zoomEnabled: true,
                    controlIconsEnabled: true,
                    fit: true,
                    center: true,
                    maxZoom: 100000,
                    minZoom: 0.1
                  });
            '''
        else:
            return ''