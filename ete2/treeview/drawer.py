import re
from ete_dev import Tree, PhyloTree, ClusterTree

# I currently use qt4 for both rendering and gui
from PyQt4  import QtGui
from qt4gui import _MainApp, _PropertiesDialog
from qt4render import _TreeScene

__all__ = ["show_tree", "render_tree", "TreeImageProperties", "NodeStyleDict"]

_QApp = None

class TreeImageProperties(object):
    def __init__(self):
        self.force_topology             = False
        self.tree_width                 = 200  # This is used to scale
                                               # the tree branches
        self.draw_aligned_faces_as_grid = True
        self.draw_lines_from_leaves_to_aligned_faces = False
        self.line_from_leaves_to_aligned_faces_type = 2 # 0 solid, 1 dashed, 2 dotted
        self.line_from_leaves_to_aligned_faces_color = "#CCCCCC"
        self.draw_image_border = False
        self.complete_branch_lines = True
        self.extra_branch_line_color = "#cccccc"
        self.show_legend = True
        self.min_branch_separation = 1 # in pixels
        self.search_node_bg = "#cccccc"
        self.search_node_fg = "#ff0000"
        self.aligned_face_header = FaceHeader()
        self.aligned_face_foot = FaceHeader()
        self.title = None
        self.botton_line_text = None

class NodeStyleDict(dict):
    _LINE_TYPE_CHECKER = lambda self, x: x in (0,1,2)
    _SIZE_CHECKER = lambda self, x: isinstance(x, int)
    _COLOR_MATCH = re.compile("^#[A-Fa-f\d]{6}$")
    _COLOR_CHECKER = lambda self, x: re.match(self._COLOR_MATCH, x)

    def __init__(self, *args, **kargs):
        super(NodeStyleDict, self).__init__(*args, **kargs)
        super(NodeStyleDict, self).__setitem__("faces", {})
        self._defaults = [
            ["fgcolor",          "#0030c1",    self._COLOR_CHECKER                           ],
            ["bgcolor",          "#FFFFFF",    self._COLOR_CHECKER                           ],
            ["vt_line_color",    "#000000",    self._COLOR_CHECKER                           ],
            ["hz_line_color",    "#000000",    self._COLOR_CHECKER                           ],
            ["line_type",        0,            self._LINE_TYPE_CHECKER                       ], # 0 solid, 1 dashed, 2 dotted
            ["size",             6,            self._SIZE_CHECKER                            ], # node circle size 
            ["shape",            "sphere",     lambda x: x in ["sphere", "circle", "square"] ], 
            ["draw_descendants", True,         lambda x: isinstance(x, bool) or x in (0,1)   ],
            ["hlwidth",          1,            self._SIZE_CHECKER                            ]
            ]
        self._valid_keys = set([i[0] for i in self._defaults]) 
        self.init()
        self._block_adding_faces = False

    def init(self):
        for key, dvalue, checker in self._defaults:
            if key not in self:
                self[key] = dvalue
            elif not checker(self[key]):
                raise ValueError("'%s' attribute in node style has not a valid value: %s" %\
                                     (key, self[key]))
        super(NodeStyleDict, self).__setitem__("_faces", {})
        # copy fixed faces to the faces dict that will be drawn 
        for pos, values in self["faces"].iteritems():
            for col, faces in values.iteritems():
                self["_faces"].setdefault(pos, {})
                self["_faces"][pos][col] = list(faces)

    def add_fixed_face(self, face, position, column):
        if self._block_adding_faces:
            raise AttributeError("fixed faces cannot be modified while drawing.")
            
        from faces import FACE_POSITIONS
        """ Add faces as a fixed feature of this node style. This
        faces are always rendered. 

        face: a Face compatible instance
        Valid positions: %s
        column: an integer number defining face relative position
         """ %FACE_POSITIONS
        self["faces"].setdefault(position, {})
        self["faces"][position].setdefault(int(column), []).append(face)

    def __setitem__(self, i, y):
        if i not in self._valid_keys:
            raise ValueError("'%s' is not a valid key for NodeStyleDict instances" %i)
        super(NodeStyleDict, self).__setitem__(i, y)

class FaceHeader(dict):
    def add_face_to_aligned_column(self, column, face):
        self.setdefault(int(column), []).append(face)

def show_tree(t, style=None, img_properties=None):
    """ Interactively shows a tree."""
    global _QApp

    if not style:
        if t.__class__ == PhyloTree:
            style = "phylogeny"
        elif t.__class__ == ClusterTree:
            style = "large"
        else:
            style = "basic"

    if not _QApp:
        _QApp = QtGui.QApplication(["ETE"])

    scene  = _TreeScene()
    mainapp = _MainApp(scene)

    if not img_properties:
        img_properties = TreeImageProperties()
    scene.initialize_tree_scene(t, style, \
                                    tree_properties=img_properties)
    scene.draw()

    mainapp.show()
    _QApp.exec_()

def render_tree(t, imgName, w=None, h=None, style=None, \
                    img_properties = None, header=None):
    """ Render tree image into a PNG file."""

    if not style:
        if t.__class__ == PhyloTree:
            style = "phylogeny"
        elif t.__class__ == ClusterTree:
            style = "large"
        else:
            style = "basic"


    global _QApp
    if not _QApp:
        _QApp = QtGui.QApplication(["ETE"])

    scene  = _TreeScene()
    if not img_properties:
        img_properties = TreeImageProperties()
    scene.initialize_tree_scene(t, style,
                                tree_properties=img_properties)
    scene.draw()
    print scene.get_tree_img_map()
    scene.save(imgName, w=w, h=h, header=header)
