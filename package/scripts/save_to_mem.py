
        # bpy.context.scene.use_nodes = True
        # tree = bpy.context.scene.node_tree
        # links = tree.links
          
        # clear default nodes
        # for n in tree.nodes:
        #     if n.name != "Composite":
        #         tree.nodes.remove(n)
        #     else:
        #         comp_node = n

          
        # create input render layer node
        # rl = tree.nodes.new('CompositorNodeRLayers')      
        # rl.location = 185,285
         
        # # create output node
        # v = tree.nodes.new('CompositorNodeViewer')   
        # v.location = 750,210
        # v.use_alpha = False
         
        # # Links
        # links.new(rl.outputs[0], v.inputs[0])  # link Image output to Viewer input
        # links.new(rl.outputs[0], comp_node.inputs[0])
        





        # # get viewer pixels
        # pixels = bpy.data.images['Viewer Node'].pixels
        # print(len(pixels)) # size is always width * height * 4 (rgba)
         
        # # copy buffer to numpy array for faster manipulation
        # arr = np.array(pixels[:])
        # total = GLOBAL_CONF['result_resolution_y'] * GLOBAL_CONF['result_resolution_x'] * 4
        # arr = arr[:total].reshape(GLOBAL_CONF['result_resolution_y'], GLOBAL_CONF['result_resolution_x'], 4)
        # print(np.unique(arr))

        # cv2.imwrite("res.png", arr[:,:,:-1])
