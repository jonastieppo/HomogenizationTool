from TexGen.Core import *
import math

# Create a textile
Textile = CTextile()

# Create a python list containing 3 yarns
Yarns = [CYarn(), CYarn(), CYarn()]

# Add nodes to the yarns to describe their paths
# First define the angled yarns
Yarns[0].AddNode(CNode(XYZ(0, 0, 0)))
Yarns[0].AddNode(CNode(XYZ(0.5, 0.2887, 0.2)))
Yarns[0].AddNode(CNode(XYZ(1, 0.5774, 0.2)))
Yarns[0].AddNode(CNode(XYZ(1.5, 0.8660, 0)))
Yarns[0].AddNode(CNode(XYZ(2, 1.1547, 0)))

Yarns[1].AddNode(CNode(XYZ(0, 0, 0.2)))
Yarns[1].AddNode(CNode(XYZ(0.5, -0.2887, 0)))
Yarns[1].AddNode(CNode(XYZ(1, -0.5774, 0)))
Yarns[1].AddNode(CNode(XYZ(1.5, -0.8660, 0.2)))
Yarns[1].AddNode(CNode(XYZ(2, -1.1547, 0.2)))

# Define a straight yarn
Yarns[2].AddNode(CNode(XYZ(-0.25, 0, 0.1)))
Yarns[2].AddNode(CNode(XYZ(-0.25, 0.57735, 0.1)))

# Create a lenticular section for the +- angled yarns
AngledSection = CSectionLenticular(0.45, 0.13)

# The section will be rotated at the appropriate points to avoid interference
# So create an interpolated yarn section
AngledYarnSection = CYarnSectionInterpPosition(True, True)
# This is the rotation angle defined
RotationAngle = math.radians(12)

# Add rotated sections at 1/8 and 5/8 of the way along the yarn
# at angles of +- RotationAngle
AngledYarnSection.AddSection(1.0/8.0, CSectionRotated(AngledSection, -RotationAngle))
AngledYarnSection.AddSection(5.0/8.0, CSectionRotated(AngledSection, RotationAngle))

# Add unrotated sections to the interpolation at intervals of 1/4
AngledYarnSection.AddSection(0.0/4.0, AngledSection)
AngledYarnSection.AddSection(1.0/4.0, AngledSection)
AngledYarnSection.AddSection(2.0/4.0, AngledSection)
AngledYarnSection.AddSection(3.0/4.0, AngledSection)

# Assign the rotating cross-section to the angled yarns
Yarns[0].AssignSection(AngledYarnSection)
Yarns[1].AssignSection(AngledYarnSection)
# Add repeats to those yarns
Yarns[0].AddRepeat(XYZ(2, 0, 0))
Yarns[1].AddRepeat(XYZ(2, 0, 0))

# Create a lenticular section for the straight yarns and assign it
StraightSection = CSectionLenticular(0.6, 0.15)
Yarns[2].AssignSection(CYarnSectionConstant(StraightSection))
# Add repeats for the straight yarn
Yarns[2].AddRepeat(XYZ(1, 0, 0))


# Loop over all the yarns in the list
for Yarn in Yarns:
    # Set the interpolation function
    Yarn.AssignInterpolation(CInterpolationCubic())
    # Set the resolution of the surface mesh created
    Yarn.SetResolution(20)
    # Add common repeat vector to the yarn
    Yarn.AddRepeat(XYZ(0, 0.57735, 0))
    # Add the yarn to our textile
    Textile.AddYarn(Yarn)

# Create a domain and assign it to the textile
Textile.AssignDomain(CDomainPlanes(XYZ(0+0.25, 0, -0.1), XYZ(1+0.25, 1, 0.3)))

# Add the textile
AddTextile("triaxialbraid", Textile)