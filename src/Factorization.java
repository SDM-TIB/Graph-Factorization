package RDFFPackage;

import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.text.ParseException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

import org.apache.jena.query.Query;
import org.apache.jena.query.QueryExecution;
import org.apache.jena.query.QueryExecutionFactory;
import org.apache.jena.query.QueryFactory;
import org.apache.jena.query.QuerySolution;
import org.apache.jena.query.ResultSet;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Resource;
import org.apache.jena.util.FileManager;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

public class Factorization {

	public static Model factorizedKG = ModelFactory.createDefaultModel();
	public static Model originalKG = ModelFactory.createDefaultModel();
	public static HashMap<String, String> uriHmap = new HashMap<String, String>();
	public static HashMap<String, String> mHmap = new HashMap<String, String>();

	public static int clusters = 0;

	public static void main(final String[] args) throws ParseException, IOException {
		final long startTime = System.currentTimeMillis();
		final String path_to_json = args[0];
		final String path_to_original_data = args[1];
		final String path_to_reduced_data = args[2];
		System.out.println("factorizing Data.....");
		factorize(path_to_json,
				path_to_original_data,
				path_to_reduced_data);
		//path_to_json: a json file containing RDF class and properties to factorize data
		//path_to_original_data: path to folder containing original RDF data
		//path_to_reduced_data: path to folder to store factorized data
		final long endTime = System.currentTimeMillis();
		final long totalTime = endTime - startTime;
		System.out.println("totalTime........." + totalTime);
	}

	public static void factorize(final String path_to_json,
			final String path_to_original_data,
			final String path_to_reduced_data) throws ParseException,
			IOException {
		final File folder = new File(path_to_original_data);
		final File[] listOfFiles = folder.listFiles();
		String inputFileName = "", outputFileName = "";
		JSONObject jsonObject = readJSON(path_to_json);
		FactorizedClass[] factorizedClasses = new FactorizedClass[jsonObject.size()];
		System.out.println("Size of class: " + factorizedClasses.length);
		int num = 0;
		if (!jsonObject.equals(null)) {
			for (Object key1 : jsonObject.keySet()) {

				String keyStr1 = (String) key1;
				Object keyvalue1 = jsonObject.get(keyStr1);
				String c = "";
				JSONArray factorizedAttributesOut = null;
				JSONArray nonfactorizedAttributesOut = null;
				JSONArray factorizedAttributesIn = null;
				JSONArray nonfactorizedAttributesIn = null;
				QHM qhfo = new QHM();// query and variable hashmap for factorized attributes outdegree
				QHM qhnfo = new QHM(); // query and variable hashmap for nonfactorized attributes outdegree
				QHM qhfi = new QHM();// query and variable hashmap for factorized attributes indegree
				QHM qhnfi = new QHM(); // query and variable hashmap for nonfactorized attributes indegree
				HashMap<String, String> mapFactorizedAttributes = new HashMap<String, String>();
				HashMap<String, String> mapNonFactorizedAttributes = new HashMap<String, String>();
				if (keyvalue1 instanceof JSONObject) {
					JSONObject jsonObject2 = (JSONObject) keyvalue1;
					for (Object key2 : jsonObject2.keySet()) {
						String keyStr2 = (String) key2;
						Object keyvalue2 = jsonObject2.get(keyStr2);
						if (keyStr2.equals("class")) {
							c = keyvalue2.toString();
							System.out.println("class is " + c);
						} else if (keyStr2.equals("factorizedAttributesOutdegree")) {
							factorizedAttributesOut = (JSONArray) keyvalue2;

						} else if (keyStr2.equals("nonfactorizedAttributesOutdegree")) {
							nonfactorizedAttributesOut = (JSONArray) keyvalue2;
							System.out.println("nonfactorized attributes are " + nonfactorizedAttributesOut);
						} else if (keyStr2.equals("factorizedAttributesIndegree")) {
							factorizedAttributesIn = (JSONArray) keyvalue2;

						} else if (keyStr2.equals("nonfactorizedAttributesIndegree")) {
							nonfactorizedAttributesIn = (JSONArray) keyvalue2;
							System.out.println("nonfactorized in attributes are " + nonfactorizedAttributesIn);
						}
					}// End of for (Object key2 : jsonObject2.keySet())
				}
				if (factorizedAttributesOut.size() != 0) {
					qhfo = buildQuery(c, factorizedAttributesOut, "out");
					if (!qhfo.getQuery().isEmpty()) {
						System.out.println("factorized outdegree query is " + qhfo.getQuery());
					} else {
						System.out.println("Factorized Outdegree Query is not returned!!!!!");
					}
				} else {
					System.out.println("Class " + c + " is not Factorizable for outdegree attributes!!!!");
				}
				if (factorizedAttributesIn.size() != 0) {
					qhfi = buildQuery(c, factorizedAttributesIn, "in");
					if (!qhfi.getQuery().isEmpty()) {
						System.out.println("factorized Indegree query is " + qhfi.getQuery());
					} else {
						System.out.println("Factorized Indegree Query is not returned!!!!!");
					}
				} else {
					System.out.println("Class " + c + " is not Factorizable for indegree attributes!!!!");
				}
				if (nonfactorizedAttributesOut.size() != 0) {
					qhnfo = buildQuery(c, nonfactorizedAttributesOut, "out");
					if (!qhnfo.getQuery().isEmpty()) {
						System.out.println("nonfactorized qhm out query is " + qhnfo.getQuery());
					} else {
						System.out.println("Query is not returned!!!!!");
					}
				} else {
					System.out.println("Class " + c + " has factorizable data only!!!!");
				}
				if (nonfactorizedAttributesIn.size() != 0) {
					qhnfi = buildQuery(c, nonfactorizedAttributesIn, "in");
					if (!qhnfi.getQuery().isEmpty()) {
						System.out.println("nonfactorized qhm in query is " + qhnfi.getQuery());
					} else {
						System.out.println("Nonfactorized in query is not returned!!!!!");
					}
				} else {
					System.out.println("Class " + c + " has no nonfactorizable data!!!!");
				}
				factorizedClasses[num] = new FactorizedClass(c, qhfo.getQuery(), qhnfo.getQuery(), qhfo.getMap(), qhnfo.getMap(), qhfi.getQuery(),
						qhnfi.getQuery(), qhfi.getMap(), qhnfi.getMap());
				num++;
			}// end of for (Object key1 : jsonObject.keySet())
		} else

		{
			System.out.println("Metadata is required!!!");
		}

		for (int i = 0; i < listOfFiles.length; i++) {
			inputFileName = outputFileName = listOfFiles[i].getName();
			inputFileName = path_to_original_data + "/" + inputFileName;
			final InputStream in = FileManager.get().open(inputFileName);
			if (in == null) { throw new IllegalArgumentException("File: " + inputFileName
					+ " not found"); }
			originalKG.read(in, null, "N3");
			System.out.println("Factorizing file: " + inputFileName);
			for (int j = 0; j < factorizedClasses.length; j++) {
				if (factorizedClasses[j].getFactorizedQueryOut() != null) {
					createMolecules(factorizedClasses[j].getClassName(), factorizedClasses[j].getFactorizedQueryOut(),
							factorizedClasses[j].getFactorizedHMOut(), "out");
				}
				if (factorizedClasses[j].getFactorizedQueryIn() != null) {
					createMolecules(factorizedClasses[j].getClassName(), factorizedClasses[j].getFactorizedQueryIn(),
							factorizedClasses[j].getFactorizedHMIn(), "in");
				}
				if (factorizedClasses[j].getNonFactorizedQueryOut() != null) {
					preserveData(factorizedClasses[j].getClassName(), factorizedClasses[j].getNonFactorizedQueryOut(),
							factorizedClasses[j].getNonFactorizedHMOut(), "out");
				}
				if (factorizedClasses[j].getNonFactorizedQueryIn() != null) {
					preserveData(factorizedClasses[j].getClassName(), factorizedClasses[j].getNonFactorizedQueryIn(),
							factorizedClasses[j].getNonFactorizedHMIn(), "in");
				}
			}

			final OutputStream out = new FileOutputStream(path_to_reduced_data + "/"
					+ outputFileName);
			System.out.println("writing to :" + path_to_reduced_data + "/"
					+ outputFileName);
			factorizedKG.write(out, "NTriples");
			originalKG.removeAll();
			factorizedKG.removeAll();
			out.close();
			in.close();
		}
		System.out.println("Total clusters created: " + clusters);

	}

	public static QHM buildQuery(final String c, final JSONArray attributes, final String direction) {
		String proj = " ?m ";
		String where = " ";
		String query = "";
		HashMap<String, String> hmap = new HashMap<String, String>();
		if (direction == "out") {
			where = where + " ?m\t<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>\t<" + c + ">.\n";
			for (int i = 0; i < attributes.size(); i++) {
				String attribute = attributes.get(i).toString();
				String var = "?v" + i;
				proj = proj + " " + var + " ";
				where = where + " ?m\t<" + attribute + ">\t" + var + ".\n";
				hmap.put(var, attribute);

			}// End of for (int i = 0; i < attributes.size(); i++)
		} else if (direction == "in") {
			where = where + " ?m\t<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>\t<" + c + ">.\n";
			for (int i = 0; i < attributes.size(); i++) {
				String attribute = attributes.get(i).toString();
				String var = "?v" + i;
				proj = proj + " " + var + " ";
				where = where + var + " \t<" + attribute + ">\t ?m" + ".\n";
				hmap.put(var, attribute);

			}// End of for (int i = 0; i < attributes.size(); i++)
		}// End of if (direction == "in")
		QHM qhm = new QHM();
		if (!where.isEmpty()) {
			query = "SELECT " + proj + " \nWHERE\n { " + where + " } ";
			qhm.setQuery(query);
			qhm.setMap(hmap);
		}
		return qhm;
	}

	public static JSONObject readJSON(final String path_to_json) throws ParseException {
		JSONParser parser = new JSONParser();
		try {
			Object obj = parser.parse(new FileReader(path_to_json));
			JSONObject jsonObject = (JSONObject) obj;
			return jsonObject;

		} catch (IOException |

				org.json.simple.parser.ParseException e) {
			e.printStackTrace();
		}
		return null;
	}

	public static void createMolecules(final String className, final String query, final HashMap hmap, final String direction) throws ParseException {

		final ResultSet results = getData(query);

		while (results.hasNext()) {
			final QuerySolution qs = results.nextSolution();
			String mid = factorizedKG.createResource(className).getLocalName();
			Set<String> keys = hmap.keySet();
			if (direction == "out") {
				for (String key : keys) {
					if (qs.get(key).isResource()) {
						String value = qs.getResource(key).getLocalName();
						mid = mid + value;
					} else {
						if (qs.get(key).toString().contains("true")) {
							String[] val = qs.get(key).toString().split("\\^\\^");
							mid = val[0];
						} else {
							String value = qs.getLiteral(key).getLexicalForm();
							if (value.contains(".")) {
								String valueStr[] = value.split(
										"\\.");
								mid = mid + valueStr[0] + "DP" + valueStr[1];
							} else {
								mid = mid + value;
							}
						}
					}
				}
				if (uriHmap.containsKey(mid)) {
					String uri = uriHmap.get(mid);
					factorizedKG
							.add(factorizedKG.createResource(uri),
									factorizedKG
											.createProperty("http://linkeddata.com/ontology#hasObservation"),
									qs.getResource("m"));
					mHmap.put(qs.getResource("m").toString(), uri);
				} else {
					String uri = "http://linkeddata.com/ontology#" + mid;
					uriHmap.put(mid, uri);
					clusters++;
					factorizedKG
							.add(factorizedKG.createResource(uri),
									factorizedKG
											.createProperty("http://linkeddata.com/ontology#hasObservation"),
									qs.getResource("m"));
					factorizedKG
							.add(factorizedKG.createResource(uri),
									factorizedKG
											.createProperty("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
									factorizedKG.createResource(className));
					Set set = hmap.entrySet();
					Iterator iterator = set.iterator();
					Resource subject = factorizedKG.createResource(uri);
					while (iterator.hasNext()) {
						Map.Entry mentry = (Map.Entry) iterator.next();
						String var = (String) mentry.getKey();
						String predicate = (String) mentry.getValue();
						if (qs.get(var).isResource()) {
							factorizedKG
									.add(subject,
											factorizedKG
													.createProperty(predicate),
											qs.getResource(var));
						} else // if (qs.get(var).isLiteral())
						{
							factorizedKG
									.add(subject,
											factorizedKG
													.createProperty(predicate),
											qs.getLiteral(var));
						}
					}
					mHmap.put(qs.getResource("m").toString(), uri);
				}
			}
			if (direction == "in") {
				String m = qs.getResource("m").toString();
				String object = mHmap.get(m);
				Set set = hmap.entrySet();
				Iterator iterator = set.iterator();
				while (iterator.hasNext()) {
					Map.Entry mentry = (Map.Entry) iterator.next();
					String var = (String) mentry.getKey();
					String predicate = (String) mentry.getValue();
					factorizedKG
							.add(qs.getResource(var),
									factorizedKG
											.createProperty(predicate),
									factorizedKG.createResource(object));
				}
			}
		}
	}

	public static void preserveData(final String className, final String query, final HashMap hmap, final String direction) throws ParseException {
		final ResultSet results = getData(query);
		while (results.hasNext()) {
			final QuerySolution qs = results.nextSolution();

			Set set = hmap.entrySet();
			Iterator iterator = set.iterator();
			Resource subject = qs.getResource("m");
			if (!mHmap.containsKey(subject.toString())) {
				factorizedKG
						.add(subject,
								factorizedKG
										.createProperty("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
								factorizedKG.createResource(className));
			}
			while (iterator.hasNext()) {

				Map.Entry mentry = (Map.Entry) iterator.next();
				String var = (String) mentry.getKey();
				String predicate = (String) mentry.getValue();
				if (direction == "out") {
					if (qs.get(var).isResource()) {
						factorizedKG
								.add(subject,
										factorizedKG
												.createProperty(predicate),
										qs.getResource(var));
					} else // if (qs.get(var).isLiteral())
					{
						factorizedKG
								.add(subject,
										factorizedKG
												.createProperty(predicate),
										qs.getLiteral(var));
					}
				} else if (direction == "in") {
					factorizedKG
							.add(qs.getResource(var),
									factorizedKG
											.createProperty(predicate),
									subject);
				}
			}
		}
	}

	public static ResultSet getData(final String query) {
		final Query queryStr = QueryFactory.create(query);
		final QueryExecution qexec = QueryExecutionFactory.create(queryStr, originalKG);
		final ResultSet result = qexec.execSelect();
		return result;
	}
}
