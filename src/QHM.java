package RDFFPackage;

import java.util.HashMap;

public class QHM {

	public String query;
	public HashMap<String, String> mapAttributes = new HashMap<String, String>();

	public void setQuery(final String query) {
		this.query = query;
	}

	public String getQuery() {
		return this.query;
	}

	public void setMap(final HashMap map) {
		this.mapAttributes = map;
	}

	public HashMap getMap() {
		return this.mapAttributes;
	}
}
