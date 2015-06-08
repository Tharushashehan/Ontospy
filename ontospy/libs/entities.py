#!/usr/bin/python
# -*- coding: utf-8 -*-

from util import *
import rdflib
from itertools import count
# http://stackoverflow.com/questions/8628123/counting-instances-of-a-class


class RDF_Entity(object):
	"""
	Pythonic representation of an RDF resource - normally not instantiated but used for 
	inheritance purposes 
	"""
	
	_ids = count(0)
			
	def __repr__(self):
		return "<OntoSPy: RDF_Entity object for uri *%s*>" % (self.uri)

	def __init__(self, uri, rdftype=None, namespaces = None):
		"""
		Init ontology object. Load the graph in memory, then setup all necessary attributes.
		"""
		self.id = self._ids.next()
		
		self.uri = uri # rdflib.Uriref
		self.qname = self.__buildQname(namespaces)	
		self.locale	 = inferURILocalSymbol(self.uri)[0]
		self.rdftype = rdftype	
		self.triples = None
		self.rdfgraph = rdflib.Graph()

		self._children = []
		self._parents = []
		# self.siblings = []
		
	def serialize(self, format="turtle"):
		if self.triples:
			if not self.rdfgraph:
				self._buildGraph()
			return self.rdfgraph.serialize(format=format)
		else:
			return None 

	def printSerialize(self, format="turtle"):
		printDebug(self.serialize(format))

	def printTriples(self):
		""" display triples """
		printDebug(bcolors.RED + unicode(self.uri) + bcolors.ENDC) 
		for x in self.triples:
			printDebug(bcolors.PINK + "=> " + unicode(x[1])) 
			printDebug(bcolors.BLUE + ".... " + unicode(x[2]) + bcolors.ENDC) 

	def __buildQname(self, namespaces):
		""" extracts a qualified name for a uri """
		return uri2niceString(self.uri, namespaces)

	def _buildGraph(self):
		""" 
		transforms the triples list into a proper rdflib graph 
		(which can be used later for querying)
		"""
		if self.triples:
			for terzetto in self.triples:
				self.rdfgraph.add(terzetto)

	# methods added to RDF_Entity even though they apply only to some subs
				
	def ancestors(self, cl=None):
		""" returns all ancestors in the taxonomy """
		if not cl:
			cl = self
		if cl.parents():
			for x in cl.parents():
				return [x] + self.ancestors(x)
		else:
			return []	
	
	def descendants(self, cl=None):
		""" returns all descendants in the taxonomy """
		if not cl:
			cl = self
		if cl.children:
			for x in cl.children:
				return [x] + self.descendants(x)
		else:
			return []

	def parents(self):
		"""wrapper around property"""
		return self._parents

	def children(self):
		"""wrapper around property"""
		return self._children

	def getproperty(self, aPropURIRef):
		""" 
		generic way to extract some prop value eg
			In [11]: c.getproperty(rdflib.RDF.type)
			Out[11]: 
			[rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#Class'),
			 rdflib.term.URIRef(u'http://www.w3.org/2000/01/rdf-schema#Class')]
		"""
		return list(self.rdfgraph.objects(None, aPropURIRef))

	def bestLabel(self):
		""" returns the best available label for an entity """
		if self.getproperty(rdflib.RDFS.label):
			return self.getproperty(RDFS.label)[0]
		elif self.getproperty(rdflib.namespace.SKOS.prefLabel):
			return self.getproperty(rdflib.namespace.SKOS.prefLabel)[0]
		else:
			return self.locale



class Ontology(RDF_Entity):
	"""
	Pythonic representation of an OWL ontology
	"""
			
	def __repr__(self):
		return "<OntoSPy: Ontology object for uri *%s*>" % (self.uri)


	def __init__(self, uri, rdftype=None, namespaces = None):
		"""
		Init ontology object. Load the graph in memory, then setup all necessary attributes.
		"""
		super(Ontology, self).__init__(uri, rdftype, namespaces)	
		# self.uri = uri # rdflib.Uriref
		self.annotations = self.triples

		self.classes = []			
		self.properties = [] 
		self.annotationProperties = [] 
		self.objectProperties = []
		self.datatypeProperties = []


	def stats(self):
		"""
		Returns a list of tuples containining interesting stats about the ontology
		"""
		out = []
		# out += [("Triples", len(self.rdfGraph))]
		out += [("Classes", len(self.classesList))]
		# out += [("Object Properties", len(self.allobjproperties))]
		# out += [("Datatype Properties", len(self.alldataproperties))]
		# out += [("Individuals", len(self.allinstances))]
		return out
		
	def classesList(self):
		print "@todo"
		return []

	def classesTree(self):
		print "@todo"

	def propertiesList(self):
		print "@todo"

	def propertiesTree(self):
		print "@todo"

	def describe(self):
		""" shotcut to pull out useful info for interactive use """
		# self.printGenericTree()
		printDebug("Classes.....: %d" % len(self.classes))
		printDebug("Properties..: %d" % len(self.properties))
		self.printTriples()





class OntoClass(RDF_Entity):
	"""
	Python representation of a generic class within an ontology. 
	Includes methods for representing and querying RDFS/OWL classes
	"""

	def __init__(self, uri, rdftype=None, namespaces=None):
		"""
		...
		"""
		super(OntoClass, self).__init__(uri, rdftype, namespaces)

		self.domain_of = []
		self.range_of = []
		
	def __repr__(self):
		return "<Class *%s*>" % ( self.uri)

	
	# @todo: does this go here? 
	def instances(self):  # = all instances
		pass

	def describe(self):
		""" shotcut to pull out useful info for interactive use """
		# self.printGenericTree()
		printDebug("Parents......: %d" % len(self.parents()))
		printDebug("Children.....: %d" % len(self.children()))
		printDebug("Ancestors....: %d" % len(self.ancestors()))
		printDebug("Descendants..: %d" % len(self.descendants()))
		printDebug("Domain of....: %d" % len(self.domain_of))
		printDebug("Range of.....: %d" % len(self.range_of))
		self.printTriples()

			
	def printGenericTree(self):
		printGenericTree(self)






class OntoProperty(RDF_Entity):
	"""
	Python representation of a generic RDF/OWL property.
	
	rdftype is one of:
	rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#ObjectProperty')
	rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#DatatypeProperty')
	rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#AnnotationProperty')
	rdflib.term.URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property')
		
	"""

	def __init__(self, uri, rdftype=None, namespaces=None):
		"""
		...
		"""
		super(OntoProperty, self).__init__(uri, rdftype, namespaces)

		self.rdftype = inferMainPropertyType(rdftype)
		
		self.domains = []
		self.ranges = []
		

	def __repr__(self):
		return "<Property *%s*>" % ( self.uri)

	
	def printPropertyTree(self):
		printGenericTree(self)


	def describe(self):
		""" shotcut to pull out useful info for interactive use """
		# self.printGenericTree()
		printDebug("Parents......: %d" % len(self.parents()))
		printDebug("Children.....: %d" % len(self.children()))
		printDebug("Ancestors....: %d" % len(self.ancestors()))
		printDebug("Descendants..: %d" % len(self.descendants()))
		printDebug("Has Domain...: %d" % len(self.domains))
		printDebug("Has Range....: %d" % len(self.ranges))		
		
		self.printTriples()
			
			