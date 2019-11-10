package RDFFPackage;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

public class FactorizedClass {

	public String className;
	public String factorizedQueryOut;
	public String nonFactorizedQueryOut;
	public HashMap<String, String> mapFactorizedAttributesOut = new HashMap<String, String>();
	public HashMap<String, String> mapNonFactorizedAttributesOut = new HashMap<String, String>();

	public String factorizedQueryIn;
	public String nonFactorizedQueryIn;
	public HashMap<String, String> mapFactorizedAttributesIn = new HashMap<String, String>();
	public HashMap<String, String> mapNonFactorizedAttributesIn = new HashMap<String, String>();

	FactorizedClass(final String className, final String factorizedQueryOut, final String nonFactorizedQueryOut, final HashMap mapFactorizedAttributesOut,
			final HashMap mapNonFactorizedAttributesOut, final String factorizedQueryIn, final String nonFactorizedQueryIn,
			final HashMap mapFactorizedAttributesIn,
			final HashMap mapNonFactorizedAttributesIn) {
		this.className = className;
		this.factorizedQueryOut = factorizedQueryOut;
		this.nonFactorizedQueryOut = nonFactorizedQueryOut;
		this.mapFactorizedAttributesOut.putAll(mapFactorizedAttributesOut);
		this.mapNonFactorizedAttributesOut.putAll(mapNonFactorizedAttributesOut);

		this.factorizedQueryIn = factorizedQueryIn;
		this.nonFactorizedQueryIn = nonFactorizedQueryIn;
		this.mapFactorizedAttributesIn.putAll(mapFactorizedAttributesIn);
		this.mapNonFactorizedAttributesIn.putAll(mapNonFactorizedAttributesIn);
	}

	public void printValues() {
		System.out.println("\n######################################\n");
		System.out.println("Class Name : " + this.className);
		System.out.println("factorizedqueryOut : " + this.factorizedQueryOut);
		System.out.println("nonFactorizedQueryOut : " + this.nonFactorizedQueryOut);

		System.out.println("mapFactorizedAttributes Outdegree are \n");
		Set set = this.mapFactorizedAttributesOut.entrySet();
		Iterator iterator = set.iterator();
		while (iterator.hasNext()) {
			Map.Entry mentry = (Map.Entry) iterator.next();
			System.out.print("key is: " + mentry.getKey() + " & Value is: ");
			System.out.println(mentry.getValue());
		}

		System.out.println("mapNonFactorizedAttributes are \n");
		Set set2 = this.mapNonFactorizedAttributesOut.entrySet();
		Iterator iterator2 = set2.iterator();
		while (iterator2.hasNext()) {
			Map.Entry mentry2 = (Map.Entry) iterator2.next();
			System.out.print("key is: " + mentry2.getKey() + " & Value is: ");
			System.out.println(mentry2.getValue());
		}
	}

	public String getFactorizedQueryOut() {
		return this.factorizedQueryOut;
	}

	public String getNonFactorizedQueryOut() {
		return this.nonFactorizedQueryOut;
	}

	public HashMap getFactorizedHMOut() {
		return this.mapFactorizedAttributesOut;
	}

	public HashMap getNonFactorizedHMOut() {
		return this.mapNonFactorizedAttributesOut;
	}

	public String getClassName() {
		return this.className;
	}

	public String getFactorizedQueryIn() {
		return this.factorizedQueryIn;
	}

	public String getNonFactorizedQueryIn() {
		return this.nonFactorizedQueryIn;
	}

	public HashMap getFactorizedHMIn() {
		return this.mapFactorizedAttributesIn;
	}

	public HashMap getNonFactorizedHMIn() {
		return this.mapNonFactorizedAttributesIn;
	}

}
