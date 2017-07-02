r"""

Pants decompositions of surfaces.

AUTHORS:

- BALAZS STRENNER (2017-05-02): initial version
- YIHAN ZHOU (2017-6-11)

EXAMPLES::

<Lots and lots of examples>


"""

#*****************************************************************************
#       Copyright (C) 2017 Balazs Strenner <strennerb@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) anys later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************


from surface import Surface
from sage.all import Graph, preparser
from train_track import TrainTrack
import collections

class PantsCoordinates(namedtuple("PantsCoordinates",
                                  "l11 l22 l33 l12 l13 l23")):
    r"""
    The `\lambda_{ij}` for a pair of pants. `\lambda_{ij}` is the
    measure of the branch connecting the boundary components i and j.
    At most three of them can be nonzero.
    """


    

class PantsDecomposition(Surface):
    """A pants decomposition of a surface.

    Pants decompositions can be encoded by a list of list. The list in the position of index i would be considered as pant i.
    Each pants is a list with 3 entries indicating 3 punctures in certain direction. Punctures are denoted by integer. Punctures of same value would be glued in the orientable direction 
    while punctures who are binary complement would be glued in opposite direction.
    
    INPUT:

    - ``p_list`` -- a list of list. The nested list should of definite length of three.
    
    EXAMPLES::

        sage: PantsDecomposition([[1,2,3],[1,2,3]])
        Pants decomposition of genus 2 orientable closed surface

        sage: PantsDecomposition([[1,2,~2]])
        Pants decomposition of klein bottle with 1 puncture

        sage: PantsDecomposition([[1,2,2]])
        Pants decomposition of torus surface with 1 puncture


    """
    def __init__(self, p_list):
        
        # punc => +-1 ~ +- inf
        # pant_name => idx

        try:
            preparser(False)
        except:
            raise ValueError('Sage preparser issue')

        num_pants = len(p_list)
        punc_map = {}
        edge_ls = []
        #gluing_cnt = 0
        gluing_set = set()
        non_ori_punc_set = set()


        for i in range(len(p_list)):
            pant = p_list[i]
            if len(pant) != 3:
                raise ValueError('One pant should have three punctures')
            for punc in pant:
                if punc == 0:
                    raise ValueError('Punctures should be named as non-zero integer')
                punc_key = abs(punc)
                if punc in punc_map.keys() and punc_map[punc][0]:
                    weight = 1
                    non_ori_punc_set.add(punc)
                else:
                    weight = 0
                if punc_key in punc_map.keys():
                    if punc_map[punc_key][1] != None and punc_map[punc_key][0] != None:
                        raise ValueError("Each puncture can only be glued once")
                    #gluing_cnt += 1
                    gluing_set.add(punc_key)
                    if punc < 0:
                        punc_map[punc_key][1] = i
                    else:
                        punc_map[punc_key][0] = i
                    edge_ls.append((punc_map[punc_key][0], punc_map[punc_key][1], weight))
                    gluing_set.add(punc_key)
                else:
                    if punc < 0:
                        punc_map[punc_key] = [None, i]
                    else:
                        punc_map[punc_key] = [i, None]

        # check for connectedness
        #print edge_ls
        g = Graph(edge_ls)

        print g

        if not g.is_connected():
            raise ValueError('Invalid input. Surface should be connect')

        # orientation
        orientable = True ### DEBUG
        #orientable = PantsDecomposition._is_orientable(g) ### DEBUG

        euler_char = -1*num_pants 
        num_puncture = num_pants*3 - 2*len(gluing_set)
        super(PantsDecomposition,self).__init__(euler_char = euler_char, num_punctures = num_puncture, is_orientable = orientable)
        #print self.__repr__()
        self._p_list = p_list
        self._p_map = punc_map
        self._gluing_set = gluing_set
        self._non_ori_punc_set = non_ori_punc_set

    def _is_orientable(g):
        orientable = True
        for cycle in g.cycle_basis(output='edge'):
            cycle_weight = sum([e[2] for e in cycle])
            if cycle_weight % 2 == 1:
                orientable = False
        return orientable


    def __repr__(self):
        return 'Pants decomposition of ' + super(PantsDecomposition,self).__repr__().lower()


    def pants_curve_as_tt(self,pants_curve):
        """
        Return a measured train track representing the pants curve.
        """
        pass
    
<<<<<<< HEAD
    def splitting_sequence_from_twist(self,curve,direction,measured_tt,power=1):
        """Return a sequence in the splitting tree for the Dehn twist.

        INPUT:

        - ``curve`` -- ``curve[:-1]`` is the list of pants curves on which a sequence of
          elementary moves are performed, and ``curve[-1]`` is the
          pants curve in the final pants decomposition on which the
          twist occurs.

        - ``direction`` -- 'left' or 'right' specifying the direction
          of the twist.
        
        - ``measured_tt`` -- a measured Dehn-Thurston train track
          whose splitting sequence is computed.

        - ``power`` -- (default:1) the power of the Dehn twist performed.

        OUTPUT:

        - a tuple (``splitting_sequence``,``carrying_map``) where both
          entries are train track maps. ``splitting_sequence`` is a
          splitting sequence from ``measured_tt`` to some train track `\tau`
          and ``carrying_map`` is a train track map from `\tau` to
          another Dehn-Thurston train track of self.
        """

        # Use self._splitting_sequence_from_elementary_move first, then
        # self._splitting_sequence_from_pants_twist, then
        # self._splitting_sequence_from_elementary_move again to change
        # back the marking, and put together the pieces.
        pass


    
    def _splitting_sequence_from_pants_twist(self,pants_curve,direction,measured_tt,power=1):
        """Return a sequence in the splitting tree for twisting about a
        pants curve.

        INPUT:

        - ``pants_curve`` -- the index of the pants curve.

        - ``direction`` -- 'L' or 'R' specifying the direction
          of the twist.
        
        - ``measured_tt`` -- a measured Dehn-Thurston train track
          whose splitting sequence is computed.

        - ``power`` -- (default:1) the power of the Dehn twist performed.

        OUTPUT:

        - a tuple (``splitting_sequence``,``carrying_map``) where both
          entries are train track maps. ``splitting_sequence`` is a
          splitting sequence from ``measured_tt`` to some train track `\tau`
          and ``carrying_map`` is a train track map from `\tau` to
          another Dehn-Thurston train track of self.

          measured_tt: t_i

        """

        t_i = measured_tt.measure()[pants_curve]

        if t_i == 0:
            pass
        elif t_i < 0 and direction == 'L':
            pass
        elif t_i > 0 and direction == 'R':
            pass

        pass

    

    def _splitting_sequence_from_elementary_move(self,pants_curve,measured_tt):
        """Return a sequence in the splitting tree for performing an
        elementary move.

        INPUT:

        - ``pants_curve`` -- the index of the pants curve on which the
          elementary move is applied.
        
        - ``measured_tt`` -- a measured Dehn-Thurston train track
          whose splitting sequence is computed.

        OUTPUT:

        - a tuple (``splitting_sequence``,``carrying_map``) where both
          entries are train track maps. ``splitting_sequence`` is a
          splitting sequence from ``measured_tt`` to some train track `\tau`
          and ``carrying_map`` is a train track map from `\tau` to
          a Dehn-Thurston train track of pants decomposition obtained
          by an elementary move.

        """
        pass

    
=======
>>>>>>> Sketch methods constructing unzipping sequences

    
        
    
    def apply_elementary_move(self,pants_curve):
        """
        Create a new pants decomposition by changing one pants curve.

        The pants have to be marked by cyclic order of the boundary
        components in each pair of pants, otherwise the elementary
        move is not uniquely specified by the pants_curve.

        INPUT:

        - ``pants_curve`` -- selected curve to apply elementary move on.

        EXAMPLES::

        Type 1 elementary move::

            sage: p1 = PantsDecomposition([[1, 2, -2]])
            sage: p1.apply_elementary_move(2)
            Pants decomposition of torus surface with 1 puncture

        The resulting (marked) pants decomposition is isomorphic to
        the original one.

        Type 2 elementary move, resulting in a pants decomposition
        with a separating curve::

            sage: p2 = PantsDecomposition([[1,2,3],[-1,-3,-2]])
            sage: p2.apply_elementary_move(1)
            Pants decomposition of genus 2 orientable closed surface

        A type 2 elementary move on the same curve of the same pants
        decomposition but with a different marking. The resulting
        pants decomposition now does not have a separating curve::

            sage: p3 = PantsDecomposition([[1,2,3],[-1,-2,-3]])
            sage: p4 = p1.apply_elementary_move(1)
            Pants decomposition of genus 2 orientable closed surface


        """
        if not self.is_orientable():
            raise NotImplementedError('Elementary move for non-orientable surface has not been implement yet.')

        curve_key = abs(pants_curve)

        if curve_key not in self._p_map.keys():
            raise ValueError('No such puncture exsit.')
        p1 = self._p_map[curve_key][0]
        p2 = self._p_map[curve_key][1]
        if p2 == None or p1 == None:
            raise ValueError('Specified curve is not glued.')
        if p1 == p2:
            return PantsDecomposition(self._p_list)
        else:
            p1_tuple = self._p_list[p1]
            p2_tuple = self._p_list[p2]
            punc_11_idx = p1_tuple.index(curve_key)
            punc_11 = p1_tuple[punc_11_idx]
            punc_21_idx = p2_tuple.index(-curve_key)
            punc_21 = p2_tuple[punc_21_idx]
            punc_12 = p1_tuple[(punc_11_idx+1)%3]
            punc_13 = p1_tuple[(punc_11_idx+2)%3]
            punc_22 = p2_tuple[(punc_21_idx+1)%3]
            punc_23 = p2_tuple[(punc_21_idx+2)%3]
            mapping_punc_dict = {}
            mapping_punc_dict[punc_12] = punc_13
            mapping_punc_dict[punc_13] = punc_22
            mapping_punc_dict[punc_22] = punc_23
            mapping_punc_dict[punc_23] = punc_12
            if -punc_12 not in mapping_punc_dict:
                mapping_punc_dict[-punc_12] = -punc_13
            if -punc_13 not in mapping_punc_dict:
                mapping_punc_dict[-punc_13] = -punc_22
            if -punc_22 not in mapping_punc_dict:
                mapping_punc_dict[-punc_22] = -punc_23
            if -punc_23 not in mapping_punc_dict:
                mapping_punc_dict[-punc_23] = -punc_12
            punc_ls = [abs(punc_11), abs(punc_12), abs(punc_13), abs(punc_22), abs(punc_23)]
            change_pant_set = set()
            rt_ls = list(self._p_list)
            for p in punc_ls:
                change_pant_set.add(self._p_map[p][0])
                if self._p_map[p][1]:
                    change_pant_set.add(self._p_map[p][1])
            for pant_idx in change_pant_set:
                cp_ls = list(rt_ls[pant_idx])
                for i in range(3):
                    ch_key = rt_ls[pant_idx][i]
                    if ch_key in mapping_punc_dict.keys():
                        cp_ls[i] = mapping_punc_dict[ch_key]
                rt_ls[pant_idx] = cp_ls
            #print rt_ls
            return PantsDecomposition(rt_ls)

      


    
    def dehn_thurston_tt(self,pants_pieces,annulus_pieces):


        """
        Return a Dehn-Thurston train track.
<<<<<<< HEAD

        INPUT:

        - ``pants_pieces`` -- list of pant type 0~3
        
        - ``annulus_pieces`` -- dictionary of connector type 'L' or 'R' 

=======
v
>>>>>>> Sketch methods constructing unzipping sequences
        EXAMPLES::

            sage: p = PantsDecomposition([[1,-1,2],[-2,4,3],[-3,5,6],[-5,-4,-6]])
            sage: p
            Pants decomposition of closed surface of genus 3
            sage: p.dehn_thurston_tt([0,0,0,0],{1:'L',2:'L',3:'R',4:'R',5:'R',6:'R'})
            Train track on surface of genus 4 with 8 punctures.
        
        For the following pants decomposition, there are only two
        Dehn-Thurston train tracks::

            sage: p = PantsDecomposition([[1,2,3],[-1,-3,-2]])
            sage: p
            Pants decomposition of closed surface of genus 2
            sage: p.dehn_thurston_tt([0,0], {1:'L',2:'L',3:'L'})
            Train track on the closed surface of genus 2
            sage: p.dehn_thurston_tt([3,1],{1:'R',2:'L',3:'R'})
            Train track on surface of genus 3 with 4 punctures.

        For the following pants decomposition, there are 16
        Dehn-Thurston train tracks (two choices for each pants and two
        choices for each pants curve)::

            sage: p = PantsDecomposition([[0,1,1,2],[0,2,1,1]])
            sage: p
            Pants decomposition of the 
            sage: p.dehn_thurston_tt([(0,1),(1,2)],[(0,1,'L'),(0,2,'R')])
            Train track on the torus with 2 punctures
            sage: p.dehn_thurston_tt([(0,2),(1,1)],[(0,1,'R'),(0,2,'L')])
            Train track on the torus with 2 punctures

        """
        #help method
        def filter_ls(ls):
            return [x for x in ls if x != 0]

        # for strange torus
        if self._genus == 1:
            raise NotImplementedError('Dehn-Thurston traintrack on torus is not implemented yet')
        else:
            train_track_ls = []

            if len(pants_pieces) != len(self._p_list):
                raise ValueError('Need to specify type for each pants')

            baseoffset = len(self._p_map)

            for punc_key in annulus_pieces.keys():

                if punc_key not in self._gluing_set:
                    raise ValueError('Selected puncture is not glued.')

                if punc_key in self._non_ori_punc_set:
                    raise NotImplementedError('Train Track for non-orientable gluing have not been implemented yet.')

                orientation = annulus_pieces[punc_key]
                # first list '+'
                if orientation == 'L':
                    p_ls_idx = self._p_map[punc_key][1]
                    p_ls_idx_neg = self._p_map[punc_key][0]
                    p_ls = self._p_list[p_ls_idx]
                    p_ls_neg = self._p_list[p_ls_idx_neg]
                    base_idx = p_ls.index(-punc_key)
                    base_idx_neg = p_ls_neg.index(punc_key)
                    p_type = pants_pieces[p_ls_idx]
                    p_type_neg = pants_pieces[p_ls_idx_neg]
                    punc_p2 = p_ls[(base_idx+1)%3]
                    punc_p3 = p_ls[(base_idx+2)%3]
                    punc_n2 = p_ls_neg[(base_idx_neg+1)%3]
                    punc_n3 = p_ls_neg[(base_idx_neg+2)%3]
                    # '+' branch
                    if p_type == 0: # type 0                       
                        train_track_ls.append(filter_ls([punc_key, -self._offset(baseoffset, punc_p2), self._offset(baseoffset, punc_p3)]))
                    elif p_type == base_idx+1: # type 1
                        train_track_ls.append(filter_ls([punc_key, -self._offset(baseoffset, punc_p2), self._offset(baseoffset, -punc_key), self._offset(baseoffset, punc_p3),-self._offset(baseoffset, -punc_key)]))
                    elif (p_type - base_idx)%3 == 2: # type 2
                        train_track_ls.append(filter_ls([punc_key, self._offset(baseoffset, punc_p3)]))
                    else: # type 3
                        train_track_ls.append(filter_ls([punc_key, -self._offset(baseoffset, punc_p2)]))
                    # '-' branch
                    if p_type_neg == 0: # type 0
                        train_track_ls.append(filter_ls([-punc_key, -self._offset(baseoffset, punc_n2), -self._offset(baseoffset, punc_n3)]))
                    elif p_type_neg == base_idx_neg+1: # type 1
                        train_track_ls.append(filter_ls([-punc_key, -self._offset(baseoffset, punc_n2), -self._offset(baseoffset, punc_key), -self._offset(baseoffset, punc_n3), -self._offset(baseoffset, punc_key)]))
                    elif (p_type_neg- base_idx_neg)%3 == 2:  # type 2
                        train_track_ls.append(filter_ls([-punc_key, -self._offset(baseoffset, punc_n3)]))
                    else: # type 3
                        train_track_ls.append(filter_ls([-punc_key, -self._offset(baseoffset, punc_n2)]))

                elif orientation == 'R':
                    p_ls_idx = self._p_map[punc_key][0]
                    p_ls_idx_neg = self._p_map[punc_key][1]
                    p_ls = self._p_list[p_ls_idx]
                    p_ls_neg = self._p_list[p_ls_idx_neg]
                    base_idx = p_ls.index(punc_key)
                    base_idx_neg = p_ls_neg.index(-punc_key)
                    p_type = pants_pieces[p_ls_idx]
                    p_type_neg = pants_pieces[p_ls_idx_neg]
                    punc_p2 = p_ls[(base_idx+1)%3]
                    punc_p3 = p_ls[(base_idx+2)%3]
                    punc_n2 = p_ls_neg[(base_idx_neg+1)%3]
                    punc_n3 = p_ls_neg[(base_idx_neg+2)%3]
                    # '+' branch
                    if p_type == 0: # type 0                      
                        train_track_ls.append(filter_ls([-self._offset(baseoffset, punc_p2), self._offset(baseoffset, punc_p3), punc_key]))
                    elif p_type == base_idx+1: # type 1 
                        train_track_ls.append(filter_ls([-self._offset(baseoffset, punc_p2), self._offset(baseoffset, -punc_key), self._offset(baseoffset, punc_p3),-self._offset(baseoffset, -punc_key), punc_key]))
                    elif (p_type - base_idx)%3 == 2: # type 2
                        train_track_ls.append(filter_ls([self._offset(baseoffset, punc_p3), punc_key]))
                    else: # type 3
                        train_track_ls.append(filter_ls([-self._offset(baseoffset, punc_p2), punc_key]))
                    # '-' branch
                    if p_type_neg == 0: # type 0    
                        train_track_ls.append(filter_ls([self._offset(baseoffset, punc_n2), -self._offset(baseoffset, punc_n3), -punc_key]))
                    elif p_type_neg == base_idx_neg+1: # type 1
                        train_track_ls.append(filter_ls([self._offset(baseoffset, punc_n2), -self._offset(baseoffset, -punc_key), -self._offset(baseoffset, punc_n3), self._offset(baseoffset, -punc_key), -punc_key]))
                    elif (p_type_neg-base_idx_neg)%3 == 2: # type 2
                        train_track_ls.append(filter_ls([-self._offset(baseoffset, punc_n3), -punc_key]))
                    else: # type 3
                        train_track_ls.append(filter_ls([self._offset(baseoffset, punc_n2), -punc_key]))
                else:
                    raise ValueError('Specify connector type by \'L\' and \'R\'')            
            
            #traintrack = TrainTrack(train_track_ls)            
            print train_track_ls
            traintrack = TrainTrack(train_track_ls)       
            #print repr(traintrack)
            return traintrack
        pass
        
    def _offset(self, baseoffset, x):
        if abs(x) in self._gluing_set:
            if x>0:
                return x + baseoffset
            else:
                return abs(x)+2*baseoffset
        else:
            return 0
    
        
    def generating_curves(self):
        """
        Return a list of curves whose twists generate.

        """
        pass
        
    
    @staticmethod
    def humphries(genus):
        """
        Construct a pants decomposition compatible with the Humphries
        generators. 

        """
        raise NotImplementedError



# class DTTrainTrack(SageObject):
#     """
#     Dehn-Thurston train track for a pants decomposition.

#     INPUT:

#     - ``pants_coordinates`` -- a list of PantsCoordinates, each
#       containing the value of `\lambda_{ij}` for the corresponding
#       pair of pants

#     - ``twist_coordinates`` -- the list of `t_i`, the twisting
#       numbers about the pants curves.

#     EXAMPLES::

#     sage: p = PantsDecomposition([[1,2,3],[-3,-2,-1]])
#     sage: p_coord = [(0,0,0,1,1,1),(0,0,1,0,1,1)]
#     sage: t_coord = [-3,2,5]
#     sage: DTTrainTrack(p,p_coord,t_coord)
#     Train track on ...
#     """

#     def __init__(self,pants_decomposition, pants_coordinates,
#                  twist_coordinates):
#         self.tt 
#         self.pants_decomposition # lambda_ij
#         self.twist_coordinates # t_i
#         self.branch_to_label_map # map from 1,...,num_branches to the
#         # t_i and l_ij


        

    
# class MeasuredLamination(SageObject):
#     pass
    

# class DehnThurstonCoordinates(MeasuredLamination):
#     """
#     Dehn-Thurston coordinates of a measured lamination.

#     EXAMPLES::

#     sage: p = PantsDecomposition([[1,2,3],[-3,-2,-1]])
#     sage: DehnThurstonCoordinates(p,[0,1,2],[1,-2,-1])
#     Measured lamination on the closed surface of genus 2

#     """
#     def __init__(self,pants_decomposition,m,t):
#         """
#         """
#         pass

#     def m(self,i):
#         """
#         Return `m_i`.
#         """
                 
#     def t(self,i):
#         """
#         Return `t_i`.
#         """

#     def l(self,i,j,pair_of_pants):
#         r"""
#         Return `\lambda_{ij}` in the specified pair of pants.

#         INPUT: 1<= i,j <=3
        
#         """

#     def pants_decomposition(self):
#         """
#         Return the underlying pants decomposition.
#         """



        


# Old Version
# class Decision(namedtuple("Decision",
#                           ["measure_A", "measure_B",
#                            "unzipping_half_branch_A_smaller", 
#                            "unzipping_half_branch_B_smaller",
#                            "next_decision_A_smaller",
#                            "next_decision_B_smaller"])): 
#     r"""A decision about where to unzip based on comparing weights.

#     We have either a measured Dehn-Thurston train track or a train
#     track obtained by unzippings from a Dehn-Thurston train track after a
#     sequence of unzippings. 

#     - ``measure_A``, ``measure_B`` -- a linear combinations of
#       measures on the branches in the original Dehn-Thurston train
#       track. For example, [('l11',2), ('t1',-1)] encodes
#       `2\lambda_{11} -t_1`.
    
#     - ``unzipping_half_branch_A_smaller`` -- the half-branch where the
#       unzipping happens if ``measure_A``<``measure_B``. For example,
#       (-5,2) means unzipping at the negative side of switch number 5
#       (on pants curve 5), to the left of the 2nd branch. If the
#       current train track is already an unzipped train track and the
#       switches are not in bijection with the pants curves, some more
#       information may be needed. 

#     - ``unzipping_half_branch_B_smaller`` -- the half-branch where the
#       unzipping happens if ``measure_B``<``measure_A``.

#     - ``next_decision_A_smaller`` -- ``None`` if no other decision is
#       needed if ``measure_A``<``measure_B``. Otherwise this is another
#       Decision object encoding the next decision.

#     - ``next_decision_A_smaller`` -- the same, taking effect when
#       ``measure_B``<``measure_A``.

#     """
#     pass

 
# class Decision(namedtuple("Decision",
#                           ["condition", "switch", "unzip_pos",
#                            "next_decisions"])): 
#     r"""A decision about where to unzip based on comparing weights.

#     We have either a measured Dehn-Thurston train track or a train
#     track obtained by unzippings from a Dehn-Thurston train track after a
#     sequence of unzippings. 

#     - ``condition`` -- e.g. 'ti < 0' or 'l11 < t_1'.
    
#     - ``switch`` -- an oriented switch, i.e. a side a switch where the
#       unzipping is performed. For type 1 moves, this should be 1 or 2.
#       For type 2, the options are 1,2,3,4 or 5. If there is a scenario
#       where a new switch is created or two switches merge, then we
#       need additional information.

#     - ``unzip_pos`` -- the index of the outgoing branch to the left of
#       which the unzipping is performed. For example, 1 means unzipping
#       between the left two branches. -1 means unzipping between the
#       right two branches.

#     - ``next_decisions`` -- a list of subsequent decisions. The cases
#       should be mutually exclusive, but they do not need to cover all
#       cases. If a case is not covered, no more decisions are made. If
#       ``None``, no more decisions are made.

#     """
#     pass


# type_1_decision_root = Decision(None,None,None,
#                                 ['first_level_decisions'])
# # TODO: Work out first level and lower level decision.

# type_2_decision_root = Decision(None,None,None,
#                                 ['first_level_decisions'])
# # TODO: Work out first level and lower level decision.
                                
                                
# # no unzippings are needed if the
# # twist is in the good direction
# left_twist_decision_root = Decision(None,None,None,[d_right])

# right_twist_decision_root = Decision(None,None,None,[d_left])

# d_left = Decision(
#     condition = 'ti < 0', # left twisting
#     switch = 1, # there is only one switch in the annulus
#     unzip_pos = 1 # unzip between outgoing branches 0 and 1. Note that
#     # outgoing branch 0 is the pants curve.
#     next_decisions = None)

# d_right = Decision(
#     condition = 'ti > 0', # right twisting
#     switch = 1, # there is only one switch in the annulus
#     unzip_pos = -1 # unzip to the left of the rightmost outgoing
#     # branch which is the pants curve. 
#     next_decisions = None)




def unzip_sequence_mapping_class(tt_map,pants_decomposition,codomain_embedding,mapping_class):
    r"""Perform unzips determined by twisting about a pants curve.

    We are handed a train track map whose domain `\mu` is any measured train
    track and whose codomain `\tau` is a Dehn-Thurston train track for some
    pants decomposition. We are also handed a mapping class `f`.

    The goal is to perform (a minimal sequence of) unzips on `\mu`
    and `\tau` to get train tracks `\mu'` and
    `\tau'`. The unzipping sequences are required to satisfy the
    following:
    - `\mu` is unzipped according to its measure and `\mu'` is a
    maximal train track (hence it is possible that non-canonical
    choices have to be made)
    - `\tau'` carries `\mu'`
    - there exists another Dehn-Thurston train track `\tau_0` for the
    same pants decomposition as '\tau` such
    that `f(\tau')` is carried on `\tau_0`,

    The method modifies the train track map from `\mu` to `\tau`
    and does not make copies. This has three separate parts:
    1. Modifying `\mu`
    2. Modifying `\tau`
    3. Modifying the ``CarryingData``

    The method creates a `\tau_0` and the ``CarryingData`` between
    `f(\tau)'` and `\tau`_0` and returns them.

    INPUT:

    - ``tt_map`` -- a TrainTrackMap whose codomain is a
      Dehn-Thurston train track and whose domain is a measured train track

    - ``pants_decomposition`` -- the pants decomposition of the
      Dehn-Thurston train track

    - ``codomain_embedding`` -- the embedding of the codomain train
      track in the pants decomposition

    - ``mapping_class`` -- a list of DehnTwists, encoding a product of
      powers of Dehn twists, read left to right

    OUTPUT:

    a Dehn-Thurston train track (`\tau_0`) and the ``CarryingData``
    for `f(\tau)` being carried on `\tau_0`.


    """
    dom = tt_map.domain
    cod = tt_map.codomain
    p = pants_decomposition

    for twist in dehn_twists:
        # changing the pants decomposition
        for move in twist.elementary_moves:
            dt_tt, codomain_embedding, cdata = \
                unzip_sequence_elementary_move(tt_map, p,
                                               codomain_embedding,
                                               move)
            # p is now the pants decomposition after the elementary
            # move. Both the domain and the codomain of tt_map are
            # changed by unzipping
            
            tt_map = TrainTrackMap(dom, dt_tt,
                                   cdata*tt_map.carrying_data)

        # applying the twist
        dt_tt, codomain_embedding, cdata = \
                unzip_sequence_pants_twist(tt_map, p,
                                           codomain_embedding,
                                           twist.pants_curve,
                                           twist.power)

        tt_map = TrainTrackMap(dom, dt_tt,
                               cdata*tt_map.carrying_data)

        # changing back the pants decomposition
        for move in reversed(twist.elementary_moves):
            dt_tt, codomain_embedding, cdata = \
                unzip_sequence_elementary_move(tt_map, p,
                                               codomain_embedding,
                                               move)
            
            tt_map = TrainTrackMap(dom, dt_tt,
                                   cdata*tt_map.carrying_data)

            # WARNING: this is probably wrong for type 1 elementary moves,
            # because applying a type 1 elementary move on the same
            # curve twice does not result in the identity (the cyclic
            # orientation in the pair of pants is reversed. So for
            # type 1 moves, the above two line may need to be
            # called three times in order to get the inverse.

    return dt_tt, codomain_embedding, cdata
        








def unzip_sequence_pants_twist(tt_map,pants_decomposition,codomain_embedding,pants_curve,power=1):
    r"""Perform unzips determined by twisting about a pants curve.

    Same as ``unzip_sequence_mapping_class``, but instead of a general
    mapping class, `f` is now a Dehn twist about a pants curve.

    INPUT:

    - ``tt_map`` -- 

    - ``pants_decomposition`` -- 

    - ``codomain_embedding`` -- 

    - ``pants_curve`` -- the index of the pants curve about which we twist

    - ``power`` -- (default:1) the power of the Dehn twist
      performed. Power `n` means right twisting `n` times. Power
      `-n` means twisting left `n` times.

    OUTPUT:

    a Dehn-Thurston train track (`\tau_0`), its embedding to the new
    pants decomposition and the ``CarryingData`` for `f(\tau)` being
    carried on `\tau_0`.

    """

    # Part 1: Trace the decision tree and perform
    # tt_map.unzip_codomain for all decisions.
    # 
    # Part 2: Create `\tau_0`. This is easy, Penner's formulas tell
    # which branches have to be drawn. More specifically, compute
    # pants_coordinates and twist_coordinates and call DTTrainTrack(pants_coordinates,twist_coordinates)
    # 
    # Part 3: Compute the CarryingData for `f(\tau)` being carried on
    # `\tau_0`. The branch-to-branch map is probably the easiest: this
    # can be read from the formulas. The half-branch-to-half-branch
    # map and the position between strands may involve
    # combinatorial/isotopy considerations. Ideally, though, the
    # branch-to-branch map uniquely determines the train track map.
    # 
    #
    # 
    #
    # 
    # ----------------------------------------
    # Without Decisions:
    dom = tt_map.domain
    cod = tt_map.codomain

    
    tt_map.compute_measure_on_codomain()
    
    if power > 0:
        if 



    if power < 0:

    pass





    
    

def unzip_sequence_elementary_move(tt_map,pants_decomposition,
                                   codomain_embedding,pants_curve):
    r"""Perform unzips determined by an elementary move on the pants decomposition.

    Same as ``unzip_sequence_mapping_class``, but instead of a mapping
    class, now we have an elementary move a pants decomposition.

    Here `\tau_0` is a Dehn-Thurston train track of the new pants
    decomposition and we want `\tau'` to be carried on `\tau_0`.

    INPUT:

    - ``tt_map`` -- 

    - ``pants_decomposition`` -- 

    - ``codomain_embedding`` -- 

    - ``pants_curve`` -- the index of the pants curve on which the
      elementary move is performed

    OUTPUT:

    a Dehn-Thurston train track (`\tau_0`), its embedding to the
    pants decomposition and the ``CarryingData``
    for `f(\tau)` being carried on `\tau_0`.

    """
    pass


class DehnTwist(namedtuple(elementary_moves,pants_curve,power)):
    """
    - ``elementary_moves`` -- a list of pants curve indices on which
    elementary moves are performed.
    
    - ``pants_curve`` -- the index of the pants curve about which we
      twist

    - ``power`` -- the power of the Dehn twist
      performed. Power `n` means right twisting `n` times. Power
      `-n` means twisting left `n` times.
    """




    
    
