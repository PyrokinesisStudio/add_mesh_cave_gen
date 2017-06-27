# GPL # Original by 'sdfgeoff' #

bl_info = {
    "name": "CaveGen",
    "author": "sdfgeoff",
    "version": (0, 1),
    "blender": (2, 6, 3),
    "location": "View3D > Add > Mesh",
    "description": "Makes Caves using metaballs converted to mesh",
    "warning": "Currently WIP",
    "category": "Add Mesh"}


import bpy
import random
from bpy.types import Operator
from bpy.props import (
        IntProperty,
        FloatProperty,
        BoolProperty,
        )


def addCave(self, context):
    print("regen Cave")

    oldLoc = [0.0, 0.0, 0.0]
    oldScale = [self.chaosx, self.chaosy, self.chaosz]
    random.seed(self.random_seed)

    print("generating initial metaball")

    bpy.ops.object.metaball_add(
                        type='BALL', view_align=False,
                        enter_editmode=True, location=(0.0, 0.0, 0.0)
                        )

    def randLoc():
        rand = (random.random() - 0.5) * 5
        if rand > 1:
            rand = 1
        if rand < -1:
            rand = -1
        return rand

    def randScale():
        rand = (random.random() * 2) + 0.2
        return rand

    def randType():
        types = ['BALL', 'ELLIPSOID', 'CAPSULE', 'CUBE']
        rand = random.choice(types)
        return rand

    def addRandLights(Prob, oldLoc, passedName, passedScene):
        print("user wants lights")
        if random.random() < Prob:
            print("create a light")
            la_lamp = bpy.data.lamps.new("la_" + passedName, 'POINT')
            la_lamp.energy = 0.1
            la_lamp.distance = 15
            ob_light = bpy.data.objects.new(passedName, la_lamp)
            ob_light.location = oldLoc
            passedScene.objects.link(ob_light)

    def generateNew(oldLoc, oldScale, run, passedScene):
        newLoc = randLoc() * oldScale[0] + oldLoc[0], \
                 randLoc() * oldScale[1] + oldLoc[1], \
                 randLoc() * oldScale[2] + oldLoc[2]

        ball = bpy.ops.object.metaball_add(type=randType(), location=(newLoc))
        if self.lights is True:
            light_name = "cave_lamp_" + str(run)
            addRandLights(self.lightProb, oldLoc, light_name, passedScene)
        """
        if random.random() > 0.9:
            createLamp(newLoc, run)
        mball = bpy.context.visible_objects[run]
        metaball = mball.data

        newScale = [randScale(), randScale(), randScale()]
        mball.scale[0] = newScale[0]
        mball.scale[1] = newScale[1]
        mball.scale[2] = newScale[2]
        """
        return newLoc, oldScale

    mball = bpy.context.selected_objects[0]
    metaball = mball.data
    metaball.resolution = 1 / self.res if self.res > 0 else 1
    metaball.render_resolution = 1 / self.res if self.res > 0 else 1
    metaball.update_method = 'NEVER'

    run = 0
    while run < self.iterations + 1:
        oldLoc, oldScale = generateNew(oldLoc, oldScale, run, context.scene)
        run += 1

    if run == 1:
        print("adding Metaballs")

    metaball.update_method = 'FAST'

    bpy.ops.object.editmode_toggle()

    if self.mesh is True:
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.vertices_smooth(repeat=2)
        bpy.ops.mesh.subdivide(number_cuts=1, fractal=5, seed=0)
        bpy.ops.mesh.vertices_smooth(repeat=1)
        bpy.ops.mesh.flip_normals()
        bpy.ops.object.editmode_toggle()


class caveGen(Operator):
    bl_idname = "mesh.primitive_cave_gen"
    bl_label = "Cave Generator"
    bl_description = "Add a Cave Mesh Object"
    bl_options = {'REGISTER', 'UNDO'}

    iterations = IntProperty(
            name="Iterations",
            default=15,
            min=2, max=10000,
            description="Sets how many metaballs to use in the cave"
            )
    chaosx = FloatProperty(
            name="Chaos X",
            default=1.0,
            min=0.1, max=2,
            description="Sets the scaling of X distance between metaballs"
            )
    chaosy = FloatProperty(
            name="Chaos Y",
            default=1.0,
            min=0.1, max=2,
            description="Sets the scaling of Y distance between metaballs"
            )
    chaosz = FloatProperty(
            name="Chaos Z",
            default=1.0,
            min=0.1, max=2,
            description="Sets the scaling of Z distance between metaballs"
            )
    res = FloatProperty(
            name="Resolution",
            default=0.8,
            min=0.1, max=10.0,
            description="Changes the resolution of the cave"
            )
    mesh = BoolProperty(
            name="Convert to mesh",
            default=True,
            description="Converts to mesh and does some subdivide/fractal functions"
            )
    lights = BoolProperty(
            name="Lights",
            default=False,
            description="Adds Lights in the passage"
            )
    lightProb = FloatProperty(
            name="Light Probability",
            default=0.1,
            min=0.001, max=1.0,
            description="Chance of a light being placed at any given point"
            )
    random_seed = IntProperty(
            name="Random Seed",
            description="Set the random seed for this cave object",
            default=101,
            min=-420, max=420
            )

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.prop(self, "mesh", toggle=True)

        col = layout.column(align=True)
        col.label("Settings:")
        col.prop(self, "iterations")
        col.prop(self, "res")

        col = layout.column(align=True)
        col.label("Randomization")
        col.prop(self, "random_seed")
        col.prop(self, "chaosx")
        col.prop(self, "chaosy")
        col.prop(self, "chaosz")

        col = layout.column(align=True)
        col.label("Lights:")
        row = col.row(align=True)
        light_icon = "OUTLINER_OB_LAMP" if self.lights else "OUTLINER_DATA_LAMP"
        row.prop(self, "lights", text="", icon=light_icon)
        row.prop(self, "lightProb")

    def execute(self, context):
        addCave(self, context)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(caveGen.bl_idname, text="Metaball Cave", icon="META_EMPTY")


def register():
    bpy.utils.register_class(caveGen)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(caveGen)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()
