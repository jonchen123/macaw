r"""



AUTHORS:

- BALAZS STRENNER (2017-07-30): initial version


"""

# *****************************************************************************
#       Copyright (C) 2017 Balazs Strenner <strennerb@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
# *****************************************************************************


# from train_track import TrainTrack
from sage.structure.sage_object import SageObject
from macaw.constants import LEFT, RIGHT, START, END, BRANCH, CUSP, \
    FORWARD, BACKWARD, INTERVAL
# from sage.all import vector
import numpy as np
from .train_track import SMALL_COLLAPSIBLE, FoldError
from .train_track0 import TrainTrack


class Click:
    """A bunch of switches of the small train track connected by infinitesimal
    branches.

    Click are always oriented so that the forward direction is the positive
    side of the switch of the corresponding switch of the large train track.

    Clicks and Intervals are linked together in a linked list.
    """
    def __init__(self):
        self.large_branch = None
        self._nb_intervals = [None, None]

    def get_interval(self, side):
        """Return the interval on the left or right.
        """
        return self._nb_intervals[side]

    def set_interval(self, side, interval):
        """Set the interval on the left or right.
        """
        self._nb_intervals[side] = interval


class Interval:
    """An interval between two Clicks in the same switch of the large train
    track.
    """
    def __init__(self):
        self.index = None
        self._nb_clicks = [None, None]

    def get_click(self, side):
        """Return the click on the left or right.
        """
        return self._nb_clicks[side]

    def set_click(self, side, click):
        """Set the click on the left or right.
        """
        self._nb_clicks[side] = click


class CarryingMap(SageObject):
    """
    A carrying relationship between two train tracks.
    """
    def __init__(self, large_tt, small_tt,
                 paths,
                 half_branch_map,
                 hb_between_branches,
                 cusp_index_offset,
                 cusp_map):
        """l = number of branches of the large train track
        s = number of branches of the small train track
        c = number of cusps of the small train track

        INPUT:

        - ``large_tt`` -- the carrying train track

        - ``small_tt`` -- the carried train track

        - ``paths`` -- [branch_paths, cusp_paths]: Two 2D arrays whose rows
        contain the branch and cusp paths of the small train
        track in the large train track. Shape: [(s, l), (c,l)].

        - ``cusp_map`` -- A 1D array specifying the image of any cusp in the
          small train track in the large train track.

        """
        self._large_tt = large_tt
        self._small_tt = small_tt

        # 2D array containing how many times paths map onto branches of the large train track and how many times they intersect intervals.
        # Rows correspond to paths, columns to branches of the large train track and intervals.
        self._path_coordinates = path_coordinates

        self._unused_interval_indices = range(10)

        # The first ``cusp_index_offset`` rows of self._transition_matrix
        # correspond to branches, the rest
        # correspond to cusps.
        self._cusp_index_offset = cusp_index_offset

        # The first ``interval_index_offset`` columns of self._transition_matrix correspond to branches of the large train track. The rest corresponds to intervals.
        self._interval_index_offset = interval_index_offset

        self._small_switch_to_click = [click1, click2]
        self._is_switch_map_orientation_preserving = [False, True]

        self._large_switch_to_extermal_interval = [
            leftmost_array, rightmost_array
        ]

        self._cusp_map = cusp_map

    # ------------------------------------------------------------------
    # CONSTRUCTORS
    # ------------------------------------------------------------------

    @classmethod
    def identity_map(cls, train_track):
        """Create a carrying map of a train track by itself.

        The large train track is the input train track, the small train track
        is a new copy.

        """
        # TODO rewrite this
        tt = train_track
        max_num_branches = tt.num_branches_if_made_trivalent()
        assert(len(tt.branches()) <= max_num_branches)

        # Identity array of arbitrary-precision Python ints.
        # Keep in mind that we fill in ones also in the rows that are not
        # actually branches.
        train_paths = np.identity(max_num_branches, dtype=object)

        half_branch_map = np.zeros((2, max_num_branches), dtype=np.int)
        for br in tt.branches():
            half_branch_map[START, br-1] = br
            half_branch_map[END, br-1] = -br

        # Initially all half-branches are at position 0 between any other
        # branchpath.
        hb_between_branches = np.zeros((2, max_num_branches, max_num_branches),
                                       dtype=object)

        max_num_switches = tt.num_switches_if_made_trivalent()

        # The number of cusps equals the number of switches for trivalent train
        # tracks, so the latter is a good number for the number of rows.
        cusp_paths = np.zeros((max_num_switches, max_num_branches),
                              dtype=object)

        cusp_end_half_branches = np.zeros(max_num_switches, dytpe=np.int)
        # branch_to_cusp = np.zeros((2, max_num_branches), dtype=np.int)
        # count = 0
        # for b in tt.branches():
        #     for sgn in [-1, 1]:
        #         br = sgn*b
        #         idx = 0 if sgn == 1 else 1
        #         sw = tt.branch_endpoint(-br)
        #         if tt.outgoing_branch(sw, 0, RIGHT) != br:
        #             branch_to_cusp[idx, b-1] = count
        #             count += 1

        switch_pos_to_cusp_idx = np.zeros(train_track._outgoing_branches.shape,
                                          dtype=np.int)
        count = 0
        for sw in tt.switches():
            for sgn in [-1, 1]:
                or_sw = sgn * sw
                idx = 0 if sgn == 1 else 1
                for pos in range(tt.num_outgoing_branches(or_sw)-1):
                    switch_pos_to_cusp_idx[idx, sw-1, pos] = count
                    count += 1

        return cls(train_track, train_track.copy(),
                   train_paths,
                   half_branch_map,
                   hb_between_branches,
                   branch_to_cusp_idx)

    # ------------------------------------------------------------------
    # GETTERS
    # ------------------------------------------------------------------

    def small_tt(self):
        return self._small_tt

    def large_tt(self):
        return self._large_tt

    def small_switch_to_click(self, small_switch):
        """Return the click containing the switch of the small train track.
        """
        return self._small_switch_to_click[abs(small_switch)-1]

    def small_cusp_to_large_cusp(self, small_cusp):
        """Return the image of a cusp of the small train track in the large
        train track.
        """
        return self._cusp_map[small_cusp-1]

    def large_cusp_to_small_cusp(self, large_cusp):
        """Return the small cusp that maps to a large cusp.
        
        OUTPUT:
        the corresponding small cusp or (if no small cusp maps to the large cusp) None
        """
        for cusp in self._small_tt.cusps():
            if self.small_cusp_to_large_cusp(cusp) == large_cusp:
                return large_cusp
        return None
    
    def interval_to_large_switch(self, interval):
        """Return the switch of the large train track containing the interval.
        """
        pass

    def click_to_large_switch(self, click):
        """Return the switch of the large train track containing the click.
        """
        pass

    def paths_in_large_branch(self, branch):
        """Return the 1D array counting the branches and cusp paths in a branch
        of the large train track.

        INPUT:

        - ``branch`` -- a branch of the large train track. Its sign does not
        matter.

        OUTPUT:

        a 1D array, containing how many times each branch and cusp path of the
        small train track shows up in this branch.

        """
        return self.get_intersections(BRANCH, branch)

    def get_intersections_with_interval(self, interval):
        """Return the intersection data of paths with a
        specified interval.
        """
        return self.get_intersections(INTERVAL, interval)

    def _path_idx(self, typ, branch_or_cusp):
        """Return the index of a branch or cusp path.
        """
        idx = abs(branch_or_cusp)-1
        if typ == CUSP:
            idx += self._cusp_index_offset
        elif typ == BRANCH:
            return idx
        assert(False)

    def _branch_or_interval_idx(self, typ, branch_or_interval):
        """Return the index of a branch of the large train track of an interval.
        """
        idx = abs(branch_or_interval)-1
        if typ == INTERVAL:
            idx += self._interval_index_offset
        elif typ == BRANCH:
            return idx
        assert(False)

    def get_intersections(self, typ, branch_or_interval):
        """Return the intersection data with large branch or and interval.
        """
        idx = self._branch_or_interval_idx(typ, branch_or_interval)
        return self._path_coordinates[:, idx]

    def path_coordinates(self, typ, branch_or_cusp):
        """Return the path coordinates (intersection with branches and intervals) of a branch or cusp of the small train track.
        """
        idx = self._path_idx(typ, branch_or_cusp)
        return self._path_coordinates[idx]

    def is_branch_or_cusp_collapsed(self, typ, branch_or_cusp):
        """Decide if a branch or cusp of the small train track is collapsed.
        """
        return np.all(self.path_coordinates(typ, branch_or_cusp) == 0)

    def is_branch_collapsed(self, branch):
        """Decide if a branch of the small train track is collapsed.
        """
        return self.is_branch_collapsed(branch)

    def is_cusp_collapsed(self, cusp):
        """Decide if a cusp of the small train track is collapsed.
        """
        return self.is_cusp_collapsed(cusp)

    # def train_path(self, typ, branch_or_cusp):
    #     """Return the train path corresponding to a branch or cusp.
    #     """
    #     idx = self._path_idx(typ, branch_or_cusp)
    #     return self._paths[idx]

    def collapsed_branches_from_small_switch(self, small_switch):
        """Return the list of collapsed branches emanating from a switch of the small train track."""
        for br in self._small_tt.outgoing_branches(small_switch):
            if self.is_branch_collapsed(br):
                yield br

    def get_connected_switches(self, branch, reversed_direction=False):
        """Return an iterator for the switches connected to the endpoint of a branch by collapsed branches. 

        The specified branch is not allowed to use as a connection. Hence the outcome is a component of a click minus a switch.
        
        The returned switches all look in the same direction as ``branch``.

        INPUT:
        - ``branch`` -- a branch of the small train track
        - ``reversed_direction`` -- leave it as False; it is only used for the recursion


        """
        switch = self._small_tt.branch_endpoint(branch)
        if reversed_direction:
            yield -switch
        else:
            yield switch
        for br in self.collapsed_branches_from_small_switch(switch):
            for sw in self.get_connected_switches(br, reversed_direction):
                yield sw

        for br in self.collapsed_branches_from_small_switch(-switch):
            if br != -branch:
                for sw in self.get_connected_switches(
                    br, not reversed_direction
                ):
                    yield sw

    def switches_in_click(self, click):
        """Return the switches of the small train track in the specified click.

        The switches will all face in the same direction as the click.
        """
        # TODO: fix orientation issue.
        for sw in self._small_tt.switches():
            if self.small_switch_to_click(sw) == click:
                return sw

    # ----------------------------------------------------------------
    # UTILITY METHODS / SETTERS
    # ----------------------------------------------------------------
    
    def append(self, typ1, append_to_num, typ2, appended_num,
               with_sign=1):
        """Update the carrying data when a train path is appended to another.
        """
        path1 = self.path_coordinates(typ1, append_to_num)
        path2 = self.path_coordinates(typ2, appended_num)
        path1 += with_sign*path2
    
    def append_path(self, typ, append_to_num, path,
               with_sign=1):
        """Update the carrying data when a train path is appended to another.

        """
        # updating the paths
        old_path = self.path_coordinates(typ, append_to_num)
        old_path += with_sign * path

    def append_in_large(self, typ1, append_to_num, typ2, appended_num, 
                                     with_sign=1):
        """Add the paths in a branch of the large train track to another branch.
        """
        x1 = self.paths_in_large_branch(add_to_branch)
        x2 = self.paths_in_large_branch(added_branch)
        x1 += with_sign * x2

    def insert_click_next_to_switch(self, small_switch, side):
        """Insert a click in the interval on the specified side of a switch of the small train track.

        The new interval (the one without intersections) is the one between the newly created click and the click of the switch.

        OUTPUT:
        - the new interval and the new click
        """
        click = self.small_switch_to_click(small_switch)
        if self._is_switch_map_orientation_preserving[abs(small_switch)-1]:
            offset = 0
        else:
            offset = 1
        interval = click.get_interval((side+offset) % 2)
        return self.insert_click_in_interval(interval, (side+offset+1) % 2)
        # TODO: This duplicates code of insert_click_in_interval() in order to retrieve offset.

    def insert_click_in_interval(self, interval, new_interval_side):
        """Create a new click and insert it in the middle of an interval.

        INPUT:
        - ``interval`` -- the interval into which the new click is inserted
        - ``new_interval_side`` -- LEFT or RIGHT, the side on which the new interval is created. ``interval`` becomes the interval on the other side

        OUTPUT:
        - the new interval and the new click
        """
        new_interval = self.create_interval()
        click = Click()
        click.set_interval((new_interval_side+1) % 2, interval)
        click.set_interval(new_interval_side, new_interval)
        right_click = interval.get_click(new_interval_side)
        new_interval.set_click(new_interval_side, right_click)
        right_click.set_interval((new_interval_side+1) % 2, new_interval)
        new_interval.set_click((new_interval_side+1) % 2, click)
        interval.set_click(new_interval_side, click)
        return new_interval, click

    def delete_click(self, click, deleted_interval_side):
        """Delete a click and the interval on the specified side of it.

        The intersections of the deleted interval are added to the intersections
        with the kept interval. The changes to the linking of clicks and intervals is also made."""
        # TODO: Wait, it should not matter which side is kept and deleted.
        ints = [click.get_interval(LEFT), click.get_interval(RIGHT)]
        kept_int = ints[(deleted_interval_side+1) % 2]
        del_int = ints[deleted_interval_side]
        self.add_interval_to_other_interval(del_int, kept_int)
        next_click = del_int.get_click(deleted_interval_side)
        kept_int.set_click(
            deleted_interval_side, next_click)
        if next_click is not None:
            next_click.set_interval((deleted_interval_side+1) % 2, kept_int)
        self.delete_interval(del_int)
        del click

    def erase_interval_intersections(self, interval):
        """Zero out the intersection data of an interval.
        """
        x = self.get_intersections_with_interval(interval)
        x.fill(0)

    def delete_interval(self, interval):
        """Delete an interval.

        This involves zeroing out all intersections, returning its index to the
        unused indices and deleting the interval object.
        """
        self.erase_interval_intersections(interval)
        self._unused_interval_indices.append(interval.index)
        # deleting explicitly because of possible circular references
        del interval

    def get_unused_interval_index(self):
        """Return an unused interval index for a new interval.
        """
        return self._unused_interval_indices.pop()


    def create_interval(self):
        interval = Interval()
        interval.index = self.get_unused_interval_index()       

    def small_switch_to_large_switch(self, small_switch):
        """Return the image of a switch of the small train track in the large
        train track.
        """
        click = self.small_switch_to_click(small_switch)
        large_switch = click.large_switch  # always positive
        if self._is_switch_map_orientation_preserving[abs(small_switch)-1]:
            return large_switch
        else:
            return -large_switch

    def interval_next_to_small_switch(self, small_switch, side):
        """Return the interval of the left of right of the small switch.
        """
        click = self.small_switch_to_click(small_switch)
        if self._is_switch_map_orientation_preserving[abs(small_switch)-1]:
            offset = 0
        else:
            offset = 1
        return click.get_interval((side+offset) % 2)
 
    def set_intersections_with_interval(self, interval, new_data):
        """Set the intersection data an interval to the specified data.
        """
        x = self.get_intersections_with_interval(interval)
        x[:] = new_data

    def add_intersection_with_interval(self, typ, branch_or_cusp, interval,
                                       with_sign=1):
        """Add an intersection of a branch or cusp with an interval (or
        subtract if ``with_sign`` is -1).
        """
        x = self.get_intersections_with_interval(interval)
        idx = self._path_idx(typ, branch_or_cusp)
        x[idx] += with_sign

    def add_intersection(self, typ1, branch_or_cusp, typ2, branch_or_interval,
                          with_sign=1):
        """Add an intersection of a small branch or cusp with a large branch or interval (or subtract if ``with_sign`` is -1).
        """
        x = self.get_intersections(typ2, branch_or_interval)
        idx = self._path_idx(typ, branch_or_cusp)
        x[idx] += with_sign

    def add_interval_to_other_interval(self, added_interval, add_to_interval,
                                       with_sign=1):
        """Add the intersection data of one interval to that of another
        interval.
        """
        x1 = self.get_intersections_with_interval(add_to_interval)
        x2 = self.get_intersections_with_interval(added_interval)
        x1 += with_sign * x2

    def set_small_switch_to_click(self, small_switch, click):
        self._small_switch_to_click[abs(small_switch)-1] = click


    def find_interval_containing_large_cusp(self, large_cusp):
        """Find the interval containing a cusp of the large train track.

        Two things can happen:
        - if a cusp of the small train track is pushed onto the large cusp, then the containing interval is not defined. This happens if and only if the cusp path corresponding to the large cusp is collapsed.
        - Otherwise there is a containing interval.

        INPUT:
        - ``large_cusp`` -- a cusp of the large train track

        OUTPUT: 
        If it is contained in an interval, then a 2-tuple is returned.
        - the interval
        - the intersection data in the right half of the interval

        If it is contained in a click, then an error is raised.
        """
        large_tt = self._large_tt
        small_tt = self._small_tt
        large_switch = large_tt.cusp_to_switch(large_cusp)

        # count the total number of strands on the left of the cusp in the
        # branches of the large train track
        count = 0
        for br in large_tt.outgoing_branches(large_switch):
            x = self.paths_in_large_branch(br)
            if count == 0:
                total = x
            else:
                total += x

            if large_tt.branch_next_to_cusp(large_cusp, LEFT) == br:
                break

        # now counting the intersections with the intervals on the left until
        # we reach the previously counted total
        interval = self.large_switch_to_extremal_interval(large_switch, LEFT)
        count = 0
        while True:
            x = self.get_intersections_with_interval(interval)
            if count == 0:
                interval_total = x
            else:
                interval_total += x

            if all(interval_total >= total):
                # we have found the right interval
                diff = interval_total-total
                return interval, diff

            def add(typ, branch_or_cusp):
                if not self.is_branch_or_cusp_collapsed(typ, branch_or_cusp):
                    idx = self._path_idx(typ, br)
                    interval_total[idx] += 1

            click = interval.get_click((RIGHT+offset) % 2)
            # TODO: fix orientation issue.
            for sw in self.switches_in_click(click):
                for br in small_tt.outgoing_branches(sw):
                    add(BRANCH, br)
                for cusp in small_tt.outgoing_cusps(sw):
                    add(CUSP, cusp)

            if all(interval_total >= total) and any(interval_total > total):
                # the cusp is not in an interval but in a click
                raise ValueError("The large cusp is contained in a click, not in an interval!")

            interval = click.get_interval((RIGHT+offset) % 2)

    def large_switch_to_extremal_interval(self, large_switch, side):
        """Return the leftmost or rightmost interval corresponding to a switch of the large train track.
        """
        offset = 0 if large_switch > 0 else 1
        return self._large_switch_to_extremal_interval[(side+1) % 2][
            abs(large_switch)-1]

    # ----------------------------------------------------------------
    # OPERATIONS
    # ----------------------------------------------------------------

    def peel_in_small(self, peeled_branch, peel_off_of, peeled_side,
                      small_switch):
        """Update the carrying map after peeling in the small train track
        """
        is_small_br_collapsed = self.is_branch_collapsed(peeled_branch)
        is_large_br_collapsed = self.is_branch_collapsed(peel_off_of)

        if not is_large_br_collapsed:
            # if the large branch was collapsed, we could still do the appends,
            # but they would not do anything.
            self.append(BRANCH, peeled_branch, BRANCH, peel_off_of)
            cusp_to_append_to = self._small_tt.adjacent_cusp(
                peeled_branch,
                side=peeled_side
            )
            self.append(CUSP, cusp_to_append_to, BRANCH, peel_off_of)

            interval = self.interval_next_to_small_switch(small_switch, LEFT)
            if not is_small_br_collapsed:
                # New intersections with an interval next to the switch are
                # only created when none of the two branches are collapsed.
                self.add_intersection_with_interval(
                    BRANCH, peeled_branch, interval)
                self.add_intersection_with_interval(
                    CUSP, cusp_to_append_to, interval)
            else:
                # If the large branch is not collapsed, but the small branch is, then our click breaks apart after the peeling.
                new_int, new_click = \
                    self.insert_click_next_to_switch(interval, RIGHT)
                for sw in self.get_connected_switches(peeled_branch):
                    self.set_small_switch_to_click(sw, new_click)

        # If the large branch is collapsed, there is nothing to do, because the peeling does not change how long the small branch is. If the small branch is also collapsed, the clicks still do not change.

    def fold_in_small(self, folded_branch, fold_onto_branch, fold_direction):
        """Perform a fold in the small train track is possible.
        """
        # Trying to isotope the endpoint of ``fold_onto_branch`` as close to the start point as possible...
        small_tt = self._small_tt
        end_sw = small_tt.branch_endpoint(fold_onto_branch)
        start_sw = small_tt.branch_endpoint(-fold_onto_branch)
        self.isotope_switch_recursively(end_sw, stop_switch=start_sw)

        # ... and isotoping the endpoint of ``folded_branch`` as far as possible.
        folded_end_sw = small_tt.branch_endpoint(folded_branch)
        self.isotope_switch_recursively(-folded_end_sw)

        # In order for the fold to be possible, after the isotopy, fold_onto_branch has to be shorter or equal than the cusp path between the folded and the fold_onto_branch. 
        # Also, the folded_branch has to be at least as long as the fold_onto_branch.
        cusp = small_tt.adjacent_cusp(folded_branch, fold_direction)
        cusp_path = self.path_coordinates(CUSP, cusp)
        fold_onto_path = self.path_coordinates(BRANCH, fold_onto_branch)
        folded_path = self.path_coordinates(BRANCH, folded_branch)
        if is_smaller_or_equal(fold_onto_path, cusp_path) and \
                is_smaller_or_equal(fold_onto_path, folded_path):
            self.append(BRANCH, folded_branch, BRANCH, fold_onto_branch, with_sign=-1)
            self.append(CUSP, cusp, BRANCH, fold_onto_branch, with_sign=-1)

            if not self.is_branch_collapsed(folded_branch):
                interval = self.interval_next_to_small_switch(
                    end_sw, fold_direction
                )
                self.add_intersection_with_interval(
                    BRANCH, folded_branch, interval, -1
                )
                self.add_intersection_with_interval(
                    CUSP, cusp, interval, -1
                )
            elif not self.self.is_branch_collapsed(fold_onto_branch):
                # Just like in the case of peeling there is a scenario
                # when clicks get merged. This happens when the folded and fold_onto branches where not collapsed but they had the same length.
                fold_onto_click = self.small_switch_to_click(fold_onto_branch)
                folded_click = self.small_switch_to_click(folded_branch)
                for sw in self.get_connected_switches(folded_branch):
                    self.set_small_switch_to_click(sw, fold_onto_click)
                self.delete_click(folded_click, RIGHT)
        else:
            raise FoldError("The folded small train track is not carried on the large train track!")

    def peel_in_large(self, peeled_branch, peel_off_of, peeled_side):
        """Update the carrying map after peeling in the large train track.

        The small train track has to be a measured train track. If there is a way to peel the large train track so that the small train track is carried, then the small train track is not changed. (In this case, the measure on the small train track does not play a role.) If there is no way to peel the large train track so that the small train track is carried, then the small train track is peeled according to the measure to make it carried. 
        """
        self.append_in_large(BRANCH, peel_off_of, BRANCH, peeled_branch, -1)

    def fold_in_large(self, folded_branch, fold_onto_branch, fold_direction):
        """Perform a fold in the large train track.
        """
        # Adding the intersections with the folded branch to fold_onto_branch.. 
        self.append_in_large(BRANCH, fold_onto_branch, BRANCH, folded_branch)
        # ... and also the left- or rightmost interval at a switch
        lg_sw = self._large_tt.branch_endpoint(fold_onto_branch)
        interval = self.large_switch_to_extremal_interval(
            lg_sw, (fold_direction+1) % 2)
        self.append_in_large(INTERVAL, interval, BRANCH, folded_branch)

        # Also add branch and interval intersection with a cusp path, since the cusp path at between the folded branches become longer.
        lg_cusp = self._large_tt.adjacent_cusp(folded_branch, fold_direction)
        sm_cusp = self.large_cusp_to_small_cusp(lg_cusp)
        self.add_intersection(CUSP, sm_cusp, BRANCH, fold_onto_branch)
        if sm_cusp != None and not self.is_cusp_collapsed(sm_cusp):
            other_int = self.find_interval_containing_large_cusp(lg_cusp)
            self.add_intersection(CUSP, sm_cusp, INTERVAL, interval)

    def delete_collapsed_branch_from_small(self, branch):
        """Update the carrying data if a branch is deleted or contracted to a
        point.
        """
        # do we need to do anything here?
        pass


    def begin_switch_isotopy(self, switch):
        """Update clicks, intervals and intersections when after the initial part of a switch isotopy.

        ---------------------------------------------------------------------
        Breaking up clicks at start
        ---------------------------------------------------------------------

        Since we move the switch from the current position, the intervals on
        the left and right of it have to be joined and the trailing branches
        added to the intersection. Only the trailing branches that were not
        collapsed are added. If the click does not go away, then some
        trailing branches might be added on the left, some might be added on
        the right. It can also happen that the click breaks apart to separate
        clicks.
        """
        large_switch = self.small_switch_to_large_switch(switch)
        if large_switch > 0:
            # Small switch maps to large switch in an orientation-preserving way.
            offset = 0
        else:
            # Small switch maps to large switch in an orientation-reversing way.
            offset = 1

        click = self.small_switch_to_click(switch)
        left_int = click.get_interval((LEFT+offset) % 2)
        backward_branches = self._small_tt.outgoing_branches(-switch)

        def add_intersections(start_idx, change, limit, interval):
            # First iterating on the backward branches in reversed order (from left to right) until we find a collapsed branch.
            for i in range(start_idx, change, limit):
                branch = backward_branches[i]
                
                # If we find a collapsed branch, we break out and iterate also start iterating from the other side.
                if self.is_branch_collapsed(branch):
                    return i

                # Otherwise we add intersections with the left-most interval.
                # First intersection with the branch.
                self.add_intersection_with_interval(
                    BRANCH, branch, interval
                )
                # Then the intersection with a cusp path.
                side = LEFT if change == -1 else RIGHT
                cusp = self._small_tt.adjacent_cusp(branch, side)
                if cusp is not None and not self.is_cusp_collapsed(cusp):
                    self.add_intersection_with_interval(
                        CUSP, cusp, interval
                    )
            return None

        last_idx = add_intersections(len(backward_branches)-1, -1, -1, left_int)

        if last_idx == None:
            # If we did not find any collapsed branches, then we remove the click, delete the interval on the right and add its intersections to the interval on the left.
            self.delete_click(click, offset)
            return
            
        right_int = click.get_interval((RIGHT+offset) % 2)
        first_idx = add_intersections(0, 1, len(backward_branches), right_int)

        idx = last_idx
        while idx != first_idx:
            branch = backward_branches[idx]

            # updating the switches belonging to the current click
            for sw in self.get_connected_switches(branch):
                self.set_small_switch_to_click(sw, click)

            # creating new click and interval on the right
            right_int, click = self.insert_click_in_interval(
                right_int, (LEFT+offset) % 2
            )

            # update intersections until we bump into the next collapsed branch
            idx = add_intersections(idx, -1, -1, right_int)

        # Finally, updating the switches belonging to the last click.
        branch = backward_branches[first_idx]
        for sw in self.get_connected_switches(branch):
            self.set_small_switch_to_click(sw, click)
        
    def end_switch_isotopy(self, switch):
        """Update clicks, intervals and intersections at the final part of a switch isotopy.

        Like at the begin_switch_isotopy() method, this involves updating intersection numbers and creating and merging clicks.
        """
        # First we need to find the switch of the large train track where the isotopy gets stuck.
        small_tt = self._small_tt
        branches = small_tt.outgoing_branches(switch)
        for br in branches:
            if self.is_branch_collapsed(br):
                next_sw = small_tt.branch_endpoint(br)
                large_switch = self.small_switch_to_large_switch(-next_sw)
                if large_switch > 0:
                    # switch maps to large_switch in an orientation-preserving way
                    offset = 0
                else:
                    # switch maps to large_switch in an orientation-reversing way
                    offset = 1
                click = self.small_switch_to_click(next_sw)
                collapsed_br = br
                break
        else:
            # There is no collapsed branch, so there must be a collapsed cusp path. This path has to be used to determine the position of
            # the switch.
            for cusp in small_tt.outgoing_cusps(switch):
                if cusp is not None and self.is_cusp_collapsed(cusp):
                    large_cusp = self.small_cusp_to_large_cusp(cusp)
                    interval, diff = self.find_interval_containing_large_cusp(
                        large_cusp
                    )
                    new_left_int, click = self.insert_click_in_interval(interval, (LEFT+offset) % 2)
                    x = self.get_intersections_with_interval(interval)
                    self.set_intersections_with_interval(new_left_int, x-diff)
                    self.set_intersections_with_interval(interval, diff)
                    collapsed_cusp = cusp
                    break
            
            current_interval = new_left_int
            # updating interval intersections of the left and right side of the switch
            for br in branches:
                self.add_intersection_with_interval(
                    BRANCH, br, current_interval, with_sign=-1)
                cusp = self.adjacent_cusp(br, RIGHT)
                if cusp is not None and not self.is_cusp_collapsed(cusp):
                    self.add_intersection_with_interval(
                        CUSP, cusp, current_interval, with_sign=-1)
                else:
                    current_interval = interval
            return

        # If we are here, then we have a collapsed branch. We still need to merge clicks and update the intersection data.

        # Updating intersections on the left
        left_int = click.get_interval((LEFT+offset) % 2)
        for br in branches:
            if br != collapsed_br:
                self.add_intersection_with_interval(BRANCH, br, left_int, -1)
            cusp = small_tt.adjacent_cusp(br, RIGHT)
            if not self.is_cusp_collapsed(cusp):
                self.add_intersection_with_interval(CUSP, cusp, left_int, -1)

        # Updating intersections on the right, 
        right_int = click.get_interval((RIGHT+offset) % 2)
        for i in range(len(branches)-1, -1, -1):
            br = branches[i]
            if self.is_branch_collapsed(br):
                break
            self.add_intersection_with_interval(BRANCH, br, right_int, -1)
            cusp = small_tt.adjacent_cusp(br, LEFT)
            if not self.is_cusp_collapsed(cusp):
                self.add_intersection_with_interval(CUSP, cusp, right_int, -1)

        # merging clicks in the middle
        while br != collapsed_br:
            if self.is_branch_collapsed(br):
                for sw in self.get_connected_switches(br):
                    self.set_small_switch_to_click(sw, click)
                current_click = self.small_switch_to_click(sw)
                self.delete_click(current_click, LEFT)
            i -= 1
            br = branches[i]

    def isotope_switch_as_far_as_possible(self, switch):
        """Isotope a switch of the small train track in the positive direction
        as far as possible.
        """
        small_tt = self._small_tt

        min_path = shortest_path(
            [self.path_coordinates(BRANCH, br) 
            for br in small_tt.outgoing_branches(switch)] +
            [self.path_coordinates(CUSP, cusp) 
            for cusp in small_tt.outgoing_cusps(switch)]
        )
        # We make a copy, otherwise subtracting a path from itself would make min_path the zero array.
        min_path = min_path.copy()

        # If no isotopy can be performed, there is nothing to do
        if np.all(min_path == 0):
            return

        # If there is non-trivial isotopy, then we begin by breaking up click at the beginning and updating the intersections.
        self.begin_switch_isotopy(switch)

        # ---------------------------------------------------------------------
        # Setting paths and intersections
        # ---------------------------------------------------------------------

        for br in small_tt.outgoing_branches(-switch):
            self.append_path(BRANCH, br, min_path)
        for cusp in small_tt.outgoing_cusps(-switch):
            self.append_path(CUSP, cusp, min_path)
        for br in small_tt.outgoing_branches(switch):
            self.append_path(BRANCH, br, min_path, with_sign=-1)
        for cusp in small_tt.outgoing_cusps(switch):
            self.append_path(CUSP, cusp, min_path, with_sign=-1)

        self.end_switch_isotopy(switch)

    def isotope_switch_recursively(self, switch, stop_switch=None):
        """Isotope a switch of the small train track as far as possible, by recursively isotoping other switches the original switch bumps into during the isotopy.

        INPUT:
        - ``switch`` -- the oriented switch which is isotoped forward
        - ``stop_switch`` -- this switch is not allowed to be isotoped. If the recursive isotopy reaches this switch, the process stops.
        """
        self.isotope_switch_as_far_as_possible(switch)
        for cusp in self._small_tt.outgoing_cusps(switch):
            if self.is_cusp_collapsed(cusp):
                # If a cusp is collapsed, there is no way to isotope further.
                return
        # If no cusp is collapsed, then we try to isotope the switches at the collapsed branches further.
        for branch in self._small_tt.outgoing_branches(switch):
            if self.is_branch_collapsed(branch):
                next_sw = -self._small_tt.branch_endpoint(branch)
                if abs(next_sw) == abs(stop_switch):
                    # We bumped into the stop_switch
                    return
                self.isotope_switch_recursively(self, next_sw)

        # After all the switches are isotoped further, we isotope the original switch as far as possible one more time.
        self.isotope_switch_as_far_as_possible(switch)
        # TODO: Do we need to do more iterations? If so, is there a way to get stuck in an infinite loop?
 






def merge_lists(a, b):
    assert(len(a) == len(b) + 1)
    ls = [a[0]]
    for i in range(len(b)):
        ls.append(b[i])
        ls.append(a[i+1])
    return ls


def is_smaller_or_equal(array1, array2):
    """Decide if all entries of the first array are less than or equal the
    corresponding entries of the second array.
    """
    assert(array1.size == array2.size)
    return all(array2-array1 >= 0)


def is_smaller(array1, array2):
    """Decide if all entries of the first array are less than the
    corresponding entries of the second array.
    """
    assert(array1.size == array2.size)
    return all(array2-array1 > 0)


def is_equal(array1, array2):
    """Decide if all entries of the first array equal corresponding entries of the
    second array.

    """
    assert(array1.size == array2.size)
    return all(array2 == array1)


def shortest_path_indices(self, paths):
    """Return the indices of shortest paths of the paths provided.

    If there is no shortest path (this is possible, since paths are arrays
    of integers, so the relation is a partial order, not an order), then it
    returns an error. But in our applications, this should not happen.

    INPUT:

    - ``paths`` -- a list of paths (arrays of integers)

    OUTPUT:

    the list of indices (between 0 and ``len(paths)-1``) of
    the shortest paths

    """

    for i in range(len(paths)):
        if all(is_smaller_or_equal(paths[i], path) for path in paths):
            break
    else:
        raise ValueError("There is no shortest path!")

    ls = [i]
    min_path = paths[i]
    for k in range(i+1, len(paths)):
        if is_equal(min_path, paths[k]):
            ls.append(k)
    return ls

def shortest_path(paths):
    """Return the shortest path of the paths provided.

    If there is no shortest path (this is possible, since paths are arrays
    of integers, so the relation is a partial order, not an order), then it
    returns an error. But in our applications, this should not happen.

    INPUT:

    - ``paths`` -- a list of paths (arrays of integers)
    
    """

    for i in range(len(paths)):
        if all(is_smaller_or_equal(paths[i], path) for path in paths):
            return paths[i]
    else:
        raise ValueError("There is no shortest path!")
