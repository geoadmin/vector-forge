# -*- coding: utf-8 -*-

from visvalingam import VisvalingamSimplification


class VisvalingamSimplificationFix(VisvalingamSimplification):

    def simplifyLineString(self, tolerance_):
        tolerance = tolerance_
        # It is enough to enrich the line once
        if(self.enriched == False):
            self.enrichLineString()
        # Build the new line
        newLine = []
        for p in self.line:
            if len(p) > 2:
                if p[2] > tolerance:
                    newLine.append(p[0:2])
            else:
                newLine.append(p)
        return newLine
